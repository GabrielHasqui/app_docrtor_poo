from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas

from aplication.core.models import Paciente
from aplication.attention.models import Atencion, DetalleAtencion, Certificado
from aplication.security.mixins.mixins import ListViewMixin


class ClinicalRecordListView(LoginRequiredMixin, ListViewMixin, ListView):
    """Vista para listar los pacientes y sus fichas clínicas"""
    template_name = "attention/clinical_record/list.html"
    model = Paciente
    context_object_name = 'patients'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Paciente.objects.filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(cedula__icontains=query)
            )
        return Paciente.objects.all()


class ClinicalRecordDetailView(LoginRequiredMixin, DetailView):
    """Vista detallada de la ficha clínica de un paciente específico"""
    model = Paciente
    template_name = 'attention/clinical_record/detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        context.update({
            'atenciones': Atencion.objects.filter(
                paciente=patient
            ).order_by('-fecha_atencion'),
            'medicamentos': DetalleAtencion.objects.filter(
                atencion__paciente=patient
            ).select_related('medicamento'),
            'certificados': Certificado.objects.filter(
                atencion__paciente=patient
            ).order_by('-fecha_emision'),
            'edad': patient.calcular_edad(patient.fecha_nacimiento)
        })

        self._add_ultima_atencion_data(context, patient)
        self._add_historial_diagnosticos(context)

        return context

    def _add_ultima_atencion_data(self, context, patient):
        ultima_atencion = patient.doctores_atencion.order_by('-fecha_atencion').first()
        if ultima_atencion:
            context['ultima_atencion'] = ultima_atencion
            if ultima_atencion.peso and ultima_atencion.altura:
                imc = float(ultima_atencion.calcular_imc)
                context['imc'] = imc
                context['imc_clasificacion'] = self._get_imc_classification(imc)

    def _get_imc_classification(self, imc):
        if imc < 18.5:
            return 'Bajo peso'
        elif 18.5 <= imc < 25:
            return 'Peso normal'
        elif 25 <= imc < 30:
            return 'Sobrepeso'
        return 'Obesidad'

    def _add_historial_diagnosticos(self, context):
        diagnosticos = set()
        for atencion in context['atenciones']:
            diagnosticos.update(atencion.diagnostico.all())
        context['historial_diagnosticos'] = list(diagnosticos)


class ImprimirHistorialClinico(View):
    def get(self, request, pk):
        paciente = Paciente.objects.get(pk=pk)
        atenciones = Atencion.objects.filter(paciente=paciente).order_by('-fecha_atencion')
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="historial_clinico_{paciente.apellidos}_{paciente.nombres}.pdf"'
        )
        
        p = canvas.Canvas(response)
        self._crear_encabezado(p, paciente)
        self._agregar_datos_personales(p, paciente)
        self._agregar_historial_medico(p, paciente)
        self._agregar_atenciones(p, atenciones)
        p.save()
        
        return response

    def _crear_encabezado(self, canvas, paciente):
        # Título principal
        canvas.setTitle(f"Historial Clínico - {paciente.nombres} {paciente.apellidos}")
        canvas.setFillColorRGB(0.2, 0.2, 0.8)  # Azul oscuro
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(50, 800, "HISTORIAL CLÍNICO COMPLETO")
        canvas.setFillColorRGB(0, 0, 0)  # Negro
        
        # Línea decorativa
        canvas.setStrokeColorRGB(0.2, 0.2, 0.8)
        canvas.setLineWidth(2)
        canvas.line(50, 790, 550, 790)

    def _agregar_datos_personales(self, canvas, paciente):
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColorRGB(0.2, 0.2, 0.8)
        canvas.drawString(50, 760, "INFORMACIÓN DEL PACIENTE")
        canvas.setFillColorRGB(0, 0, 0)
        
        # Datos personales
        data = [
            ("Nombre completo:", f"{paciente.nombres} {paciente.apellidos}"),
            ("Cédula:", paciente.cedula),
            ("Fecha de nacimiento:", paciente.fecha_nacimiento.strftime("%d/%m/%Y")),
            ("Edad:", f"{paciente.calcular_edad(paciente.fecha_nacimiento)} años"),
            ("Sexo:", paciente.get_sexo_display()),
            ("Estado civil:", paciente.get_estado_civil_display()),
            ("Teléfono:", paciente.telefono),
            ("Email:", paciente.email or "No registrado"),
            ("Dirección:", paciente.direccion)
        ]
        
        y = 740
        for label, value in data:
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(50, y, label)
            canvas.setFont("Helvetica", 10)
            canvas.drawString(170, y, str(value))
            y -= 20

    def _agregar_historial_medico(self, canvas, paciente):
        y = 560
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColorRGB(0.2, 0.2, 0.8)
        canvas.drawString(50, y, "HISTORIAL MÉDICO BÁSICO")
        canvas.setFillColorRGB(0, 0, 0)
        y -= 20
        
        datos_medicos = [
            ("Tipo de sangre:", paciente.tipo_sangre.tipo if paciente.tipo_sangre else "No registrado"),
            ("Alergias:", paciente.alergias or "Ninguna registrada"),
            ("Enfermedades crónicas:", paciente.enfermedades_cronicas or "Ninguna registrada"),
            ("Medicación actual:", paciente.medicacion_actual or "Ninguna"),
            ("Cirugías previas:", paciente.cirugias_previas or "Ninguna registrada"),
        ]
        
        for label, value in datos_medicos:
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(50, y, label)
            canvas.setFont("Helvetica", 10)
            canvas.drawString(170, y, str(value))
            y -= 20

    def _agregar_atenciones(self, canvas, atenciones):
        y = 440
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColorRGB(0.2, 0.2, 0.8)
        canvas.drawString(50, y, "HISTORIAL DE ATENCIONES MÉDICAS")
        canvas.setFillColorRGB(0, 0, 0)
        y -= 30
        
        for atencion in atenciones:
            if y < 50:  # Nueva página si no hay espacio
                canvas.showPage()
                y = 800
            
            # Fecha y motivo
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawString(50, y, f"Fecha de atención: {atencion.fecha_atencion.strftime('%d/%m/%Y %H:%M')}")
            y -= 20
            
            # Signos vitales
            canvas.setFont("Helvetica", 10)
            signos = [
                f"Presión arterial: {atencion.presion_arterial or 'NR'}",
                f"Temperatura: {atencion.temperatura or 'NR'}°C",
                f"Peso: {atencion.peso or 'NR'} kg",
                f"Altura: {atencion.altura or 'NR'} m",
                f"IMC: {atencion.calcular_imc or 'NR'}"
            ]
            for signo in signos:
                canvas.drawString(70, y, signo)
                y -= 15
            
            # Motivo y diagnósticos
            canvas.drawString(70, y, f"Motivo de consulta: {atencion.motivo_consulta}")
            y -= 15
            canvas.drawString(70, y, f"Síntomas: {atencion.sintomas}")
            y -= 15
            canvas.drawString(70, y, f"Diagnósticos: {', '.join([d.descripcion for d in atencion.diagnostico.all()])}")
            y -= 15
            canvas.drawString(70, y, f"Tratamiento: {atencion.tratamiento}")
            
            # Línea separadora entre atenciones
            y -= 25
            canvas.setLineWidth(1)
            canvas.line(50, y, 550, y)
            y -= 25