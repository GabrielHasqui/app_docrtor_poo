from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.shortcuts import redirect
from django.http import JsonResponse
from aplication.attention.models import Certificado
from aplication.core.models import Doctor
from aplication.attention.forms.certificate import CertificateForm
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
import textwrap


class CertificateListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "attention/certificates/list.html"
    model = Certificado
    context_object_name = 'certificates'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Certificado.objects.filter(
                Q(atencion__paciente__nombre__icontains=query) |
                Q(tipo_certificado__icontains=query)
            )
        return Certificado.objects.all()

class CertificateCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Certificado
    template_name = 'attention/certificates/form.html'
    form_class = CertificateForm
    success_url = reverse_lazy('attention:certificate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Grabar Certificado'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        certificate = self.object
        save_audit(self.request, certificate, action='A')
        messages.success(self.request, f"Éxito al crear el certificado para {certificate.atencion.paciente}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class CertificateUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Certificado
    template_name = 'attention/certificates/form.html'
    form_class = CertificateForm
    success_url = reverse_lazy('attention:certificate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Certificado'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        certificate = self.object
        save_audit(self.request, certificate, action='M')
        messages.success(self.request, f"Éxito al modificar el certificado para {certificate.atencion.paciente}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class CertificateDeleteView(DeleteView, DeleteViewMixin, LoginRequiredMixin):
    model = Certificado
    template_name = 'attention/certificates/delete.html'
    success_url = reverse_lazy('attention:certificate_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Certificado eliminado con éxito.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, "Este certificado no se puede eliminar porque está en uso.")
            return redirect(self.success_url)

class CertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificado

    def get(self, request, *args, **kwargs):
        certificate = self.get_object()
        data = {
            'id': certificate.id,
            'atencion': certificate.atencion.paciente.nombres,
            'tipo_certificado': certificate.tipo_certificado,
            'fecha_emision': certificate.fecha_emision.strftime('%Y-%m-%d %H:%M'),
            'descripcion': certificate.descripcion,
        }
        return JsonResponse(data)

class CertificatePDFView(LoginRequiredMixin, DetailView):
    model = Certificado

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        certificate = self.object
        try:
            doctor = Doctor.objects.get(cedula="0951777838")
            especialidad = getattr(doctor.especialidad.first(), 'nombre', 'No especificada')
        except Doctor.DoesNotExist:
            messages.error(request, "No se encontró información del doctor.")
            return redirect('attention:certificate_list')
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        width, height = 595.27, 841.89  # A4

        # Document setup
        p.setTitle("Certificado Médico Oficial")
        
        # Header with gradient-like effect
        for i in range(120):
            p.setFillColorRGB(0, 0, 0.6 - i/400)
            p.rect(0, height-(120-i), width, 1, fill=True)

        # Professional header
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 26)
        p.drawString(120, height-70, "CERTIFICADO MÉDICO OFICIAL")
        
        # Doctor info with styled box
        p.setFillColorRGB(0.95, 0.95, 1)
        p.roundRect(40, height-160, width-80, 60, 10, fill=True)
        p.setFillColorRGB(0.2, 0.2, 0.5)
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, height-130, f"Dr. {doctor.nombre_completo}")
        p.setFont("Helvetica", 12)
        p.drawString(50, height-150, f"Especialidad en {especialidad}")

        # Certificate details with styled container
        y_position = height-200
        p.setFillColorRGB(0.97, 0.97, 1)
        p.roundRect(40, y_position-120, width-80, 100, 8, fill=True)
        
        # Details content
        p.setFillColorRGB(0.1, 0.1, 0.4)
        p.setFont("Helvetica-Bold", 11)
        details = [
            f"Nº de Certificado: {certificate.id}",
            f"Paciente: {certificate.atencion.paciente.nombres}",
            f"Tipo: {certificate.tipo_certificado}",
            f"Emitido: {certificate.fecha_emision.strftime('%d de %B del %Y - %H:%M')}"
        ]
        for i, detail in enumerate(details):
            p.drawString(50, y_position-40-(i*20), detail)

        # Description section
        p.setFillColorRGB(0.97, 0.97, 1)
        p.roundRect(40, y_position-350, width-80, 180, 8, fill=True)
        
        p.setFillColorRGB(0.1, 0.1, 0.4)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position-190, "CERTIFICO QUE:")
        
        # Description text with proper wrapping
        p.setFont("Helvetica", 11)
        text = p.beginText(60, y_position-220)
        wrapped_text = "\n".join(textwrap.wrap(certificate.descripcion, 80))
        for line in wrapped_text.splitlines():
            text.textLine(line)
        p.drawText(text)

        # Footer design
        p.setFillColorRGB(0.1, 0.3, 0.6)
        p.rect(40, 120, width-80, 1, fill=True)
        
        # Signature section
        if doctor.firmaDigital:
            p.drawImage(doctor.firmaDigital.path, width-250, 130, width=200, height=100, preserveAspectRatio=True)
        
        p.setFont("Helvetica-Bold", 10)
        p.drawString(width-250, 115, f"Dr. {doctor.nombre_completo}")
        p.setFont("Helvetica", 9)
        p.drawString(width-250, 100, f"Especialista en {especialidad}")
        p.drawString(width-250, 85, f"Reg. Profesional: {doctor.cedula}")

        # QR Code or validation info
        p.setFillColorRGB(0.5, 0.5, 0.5)
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 50, "Este documento es un certificado médico oficial. Validación digital disponible.")
        p.drawString(50, 35, f"Documento generado el {certificate.fecha_emision.strftime('%d/%m/%Y a las %H:%M')}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='certificado_medico.pdf')