import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from aplication.attention.forms.examination_form import ExamenForm
from aplication.attention.forms.medical_attention import AttentionForm
from aplication.attention.models import Atencion, DetalleAtencion, DetalleExamen, Examen, Factura, ServicioAtencion, ServiciosAdicionales
from aplication.core.models import Diagnostico, Medicamento
from doctor import settings
from doctor.mixins import CreateViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import custom_serializer, save_audit
from paypalrestsdk import Payment

class AttentionListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "attention/medical_attention/list.html"
    model = Atencion
    context_object_name = "atenciones"

    def get_queryset(self):
        # self.query = Q()
        q1 = self.request.GET.get("q")  # ver
        sex = self.request.GET.get("sex")
        if q1 is not None:
            self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
            self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
            self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)
        if sex == "M" or sex == "F":
            self.query.add(Q(paciente__sexo__icontains=sex), Q.AND)
        return self.model.objects.filter(self.query).order_by("-fecha_atencion")

class AttentionCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Atencion
    template_name = "attention/medical_attention/form.html"
    form_class = AttentionForm
    success_url = reverse_lazy("attention:attention_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        
        # Get active records for dropdowns
        context["medications"] = Medicamento.active_medication.values(
            "id", "nombre"
        ).order_by("nombre")
        context["examenes"] = Examen.objects.all().values(
            "id", "tipo_examen", "descripcion", "precio"
        ).order_by("tipo_examen")
        context["servicios"] = ServiciosAdicionales.objects.filter(activo=True).values(
            "id", "nombre_servicio", "costo_servicio"
        ).order_by("nombre_servicio")

        # Initialize empty lists for new attention
        context["detail_atencion"] = json.dumps([], default=custom_serializer)
        context["detail_examenes"] = json.dumps([], default=custom_serializer)
        context["detail_servicios"] = json.dumps([], default=custom_serializer)

        return context

    def generar_numero_factura(self):
        """Genera un número de factura único"""
        ultimo_numero = Factura.objects.order_by('-numero_factura').first()
        if ultimo_numero:
            try:
                numero = int(ultimo_numero.numero_factura) + 1
            except ValueError:
                numero = 1
        else:
            numero = 1
        return str(numero).zfill(8)

    def crear_factura(self, atencion):
        """Crea una nueva factura para la atención"""
        factura = Factura.objects.create(
            atencion=atencion,
            numero_factura=self.generar_numero_factura(),
            estado='BORRADOR'
        )
        factura.generar_detalles()
        return factura

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            with transaction.atomic():
                # Create main attention record
                atencion = Atencion.objects.create(
                    paciente_id=int(data["paciente"]),
                    presion_arterial=data["presionArterial"],
                    pulso=int(data["pulso"]),
                    temperatura=Decimal(data["temperatura"]),
                    frecuencia_respiratoria=int(data["frecuenciaRespiratoria"]),
                    saturacion_oxigeno=Decimal(data["saturacionOxigeno"]),
                    peso=Decimal(data["peso"]),
                    altura=Decimal(data["altura"]),
                    motivo_consulta=data["motivoConsulta"],
                    sintomas=data["sintomas"],
                    tratamiento=data["tratamiento"],
                    examen_fisico=data["examenFisico"],
                    examenes_enviados=data["examenesEnviados"],
                    comentario_adicional=data["comentarioAdicional"],
                    valor_consulta=Decimal(data.get("valorConsulta", "0.00"))
                )

                # Add diagnósticos
                diagnostico_ids = data.get("diagnostico", [])
                diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
                atencion.diagnostico.set(diagnosticos)

                # Create medications
                for medicamento in data.get("medicamentos", []):
                    DetalleAtencion.objects.create(
                        atencion=atencion,
                        medicamento_id=int(medicamento["codigo"]),
                        cantidad=int(medicamento["cantidad"]),
                        prescripcion=medicamento["prescripcion"],
                        duracion_tratamiento=medicamento.get("duracion", None)
                    )

                # Create examinations
                for examen in data.get("examenes", []):
                    DetalleExamen.objects.create(
                        atencion=atencion,
                        examen_id=int(examen["codigo"]),
                        resultado=examen.get("resultado", "Pendiente"),
                        activo=True
                    )

                # Create services
                for servicio in data.get("servicios", []):
                    ServicioAtencion.objects.create(
                        atencion=atencion,
                        servicio_id=int(servicio["codigo"]),
                        cantidad=int(servicio.get("cantidad", 1))
                    )

                # Create invoice
                factura = self.crear_factura(atencion)

                save_audit(request, atencion, "C")
                messages.success(
                    self.request,
                    f"Éxito al crear la atención médica #{atencion.id} y generar factura #{factura.numero_factura}",
                )
                return JsonResponse({
                    "msg": "Éxito al crear la atención médica.",
                    "atencion_id": atencion.id,
                    "factura_id": factura.id,
                    "numero_factura": factura.numero_factura
                }, status=200)

        except Exception as ex:
            messages.error(self.request, f"Error al crear la atención médica")
            return JsonResponse({"msg": str(ex)}, status=400)


class AttentionUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Atencion
    template_name = "attention/medical_attention/form.html"
    form_class = AttentionForm
    success_url = reverse_lazy("attention:attention_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        
        # Get active records for dropdowns
        context["medications"] = Medicamento.active_medication.values(
            "id", "nombre"
        ).order_by("nombre")
        context["examenes"] = Examen.objects.all().values(
            "id", "tipo_examen", "descripcion", "precio"
        ).order_by("tipo_examen")
        context["servicios"] = ServiciosAdicionales.objects.filter(activo=True).values(
            "id", "nombre_servicio", "costo_servicio"
        ).order_by("nombre_servicio")

        # Get existing details
        detail_atencion = list(
            DetalleAtencion.objects.filter(atencion_id=self.object.id).values(
                "medicamento_id", "medicamento__nombre", "cantidad", "prescripcion", 
                "duracion_tratamiento"
            )
        )

        detail_examenes = list(
            DetalleExamen.objects.filter(atencion_id=self.object.id, activo=True).values(
                "examen_id", "examen__tipo_examen", "examen__descripcion", 
                "resultado", "fecha_realizacion"
            )
        )

        detail_servicios = list(
            ServicioAtencion.objects.filter(atencion_id=self.object.id).values(
                "servicio_id", "servicio__nombre_servicio", "cantidad",
                "servicio__costo_servicio"
            )
        )

        # Convert to JSON for template
        context["detail_atencion"] = json.dumps(detail_atencion, default=custom_serializer)
        context["detail_examenes"] = json.dumps(detail_examenes, default=custom_serializer)
        context["detail_servicios"] = json.dumps(detail_servicios, default=custom_serializer)

        return context

    def generar_numero_factura(self):
        """Genera un número de factura único"""
        ultimo_numero = Factura.objects.order_by('-numero_factura').first()
        if ultimo_numero:
            try:
                numero = int(ultimo_numero.numero_factura) + 1
            except ValueError:
                numero = 1
        else:
            numero = 1
        return str(numero).zfill(8)

    def crear_actualizar_factura(self, atencion):
        """Crea o actualiza la factura asociada a la atención"""
        try:
            factura = atencion.factura
        except Factura.DoesNotExist:
            factura = Factura.objects.create(
                atencion=atencion,
                numero_factura=self.generar_numero_factura(),
                estado='BORRADOR'
            )
        
        factura.generar_detalles()
        return factura

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            atencion = self.get_object()
            with transaction.atomic():
                # Update main attention record
                atencion.paciente_id = int(data["paciente"])
                atencion.presion_arterial = data["presionArterial"]
                atencion.pulso = int(data["pulso"])
                atencion.temperatura = Decimal(data["temperatura"])
                atencion.frecuencia_respiratoria = int(data["frecuenciaRespiratoria"])
                atencion.saturacion_oxigeno = Decimal(data["saturacionOxigeno"])
                atencion.peso = Decimal(data["peso"])
                atencion.altura = Decimal(data["altura"])
                atencion.motivo_consulta = data["motivoConsulta"]
                atencion.sintomas = data["sintomas"]
                atencion.tratamiento = data["tratamiento"]
                atencion.examen_fisico = data["examenFisico"]
                atencion.examenes_enviados = data["examenesEnviados"]
                atencion.comentario_adicional = data["comentarioAdicional"]
                atencion.valor_consulta = Decimal(data.get("valorConsulta", "0.00"))

                # Update diagnósticos
                diagnostico_ids = data.get("diagnostico", [])
                diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
                atencion.diagnostico.set(diagnosticos)
                atencion.save()

                # Update medications
                DetalleAtencion.objects.filter(atencion_id=atencion.id).delete()
                for medicamento in data.get("medicamentos", []):
                    DetalleAtencion.objects.create(
                        atencion=atencion,
                        medicamento_id=int(medicamento["codigo"]),
                        cantidad=int(medicamento["cantidad"]),
                        prescripcion=medicamento["prescripcion"],
                        duracion_tratamiento=medicamento.get("duracion", None)
                    )

                # Update examinations
                DetalleExamen.objects.filter(atencion_id=atencion.id).update(activo=False)
                for examen in data.get("examenes", []):
                    DetalleExamen.objects.create(
                        atencion=atencion,
                        examen_id=int(examen["codigo"]),
                        resultado=examen.get("resultado", "Pendiente"),
                        activo=True
                    )

                # Update services
                ServicioAtencion.objects.filter(atencion_id=atencion.id).delete()
                for servicio in data.get("servicios", []):
                    ServicioAtencion.objects.create(
                        atencion=atencion,
                        servicio_id=int(servicio["codigo"]),
                        cantidad=int(servicio.get("cantidad", 1))
                    )

                # Create or update invoice
                factura = self.crear_actualizar_factura(atencion)

                save_audit(request, atencion, "M")
                messages.success(
                    self.request,
                    f"Éxito al Actualizar la atención médica #{atencion.id} y generar factura #{factura.numero_factura}",
                )
                return JsonResponse({
                    "msg": "Éxito al Actualizar la atención médica.",
                    "factura_id": factura.id,
                    "numero_factura": factura.numero_factura
                }, status=200)
        except Exception as ex:
            messages.error(self.request, f"Error al actualizar la atención médica")
            return JsonResponse({"msg": str(ex)}, status=400)
class AttentionDetailView(LoginRequiredMixin, DetailView):
    model = Atencion

    def get(self, request, *args, **kwargs):
        atencion = self.get_object()
        
        # Get details for medications
        detail_atencion = list(
            DetalleAtencion.objects.filter(atencion_id=atencion.id).values(
                "medicamento_id", "medicamento__nombre", "cantidad", "prescripcion"
            )
        )

        # Get details for examinations
        detail_examenes = list(
            DetalleExamen.objects.filter(atencion_id=atencion.id, activo=True).values(
                "examen_id", "examen__tipo_examen", "resultado", "fecha_realizacion"
            )
        )

        # Get details for services
        detail_servicios = list(
            ServicioAtencion.objects.filter(atencion_id=atencion.id).values(
                "servicio_id", "servicio__nombre_servicio", "cantidad",
                "subtotal"
            )
        )

        data = {
            "id": atencion.id,
            "nombres": atencion.paciente.nombre_completo,
            "foto": atencion.paciente.get_image(),
            "detalle_atencion": json.dumps(detail_atencion, default=custom_serializer),
            "detalle_examenes": json.dumps(detail_examenes, default=custom_serializer),
            "detalle_servicios": json.dumps(detail_servicios, default=custom_serializer),
            "valor_consulta": str(atencion.valor_consulta),
            "total_medicamentos": str(atencion.get_total_medicamentos()),
            "total_examenes": str(atencion.get_total_examenes()),
            "total_servicios": str(atencion.get_total_servicios()),
            "total_general": str(atencion.get_total_atencion())
        }
        
        return JsonResponse(data)
    
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import JsonResponse
from django.db import transaction
import json

from aplication.attention.forms.examination_form import ExamenForm
from aplication.attention.models import Examen
from doctor.mixins import CreateViewMixin

class ExaminationCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Examen
    form_class = ExamenForm
    template_name = "attention/examination/form.html"
    # success_url = reverse_lazy("attention:examen_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Registrar'
        context['back_url'] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            with transaction.atomic():
                examen = Examen.objects.create(
                    tipo_examen=data["tipo_examen"],
                    descripcion=data["descripcion"],
                    precio=data["precio"]
                )
                
                save_audit(request, examen, "A")
                messages.success(
                    request,
                    f"Éxito al registrar el examen {examen.tipo_examen}"
                )
                return JsonResponse({"msg": "Éxito al registrar el examen."}, status=200)
        except Exception as ex:
            messages.error(request, "Error al registrar el examen")
            return JsonResponse({"msg": str(ex)}, status=400)
# class ExaminationUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
#     model = DetalleExamen
#     template_name = "attention/examination/form.html"
#     success_url = reverse_lazy("attention:examination_list")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["examenes"] = Examen.objects.filter(activo=True).order_by('tipo_examen')
#         context["atenciones"] = Atencion.objects.all().order_by('-fecha_atencion')
#         return context

#     def post(self, request, *args, **kwargs):
#         data = json.loads(request.body)
#         try:
#             with transaction.atomic():
#                 detalle_examen = self.get_object()
#                 detalle_examen.atencion_id = int(data["atencion"])
#                 detalle_examen.examen_id = int(data["examen"])
#                 detalle_examen.resultado = data["resultado"]
#                 detalle_examen.save()

#                 save_audit(request, detalle_examen, "M")
#                 messages.success(
#                     request,
#                     f"Éxito al actualizar el examen #{detalle_examen.id}"
#                 )
#                 return JsonResponse({"msg": "Éxito al actualizar el examen."}, status=200)
#         except Exception as ex:
#             messages.error(request, "Error al actualizar el examen")
#             return JsonResponse({"msg": str(ex)}, status=400)

class InvoiceCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Factura
    template_name = "attention/invoice/form.html"
    # success_url = reverse_lazy("attention:invoice_list")
    fields = ['atencion', 'numero_factura']  # Agrega este atributo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["atenciones"] = Atencion.objects.all().order_by('-fecha_atencion')
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            with transaction.atomic():
                factura = Factura.objects.create(
                    atencion_id=int(data["atencion"]),
                    numero_factura=data["numero_factura"],
                )
                
                # Generar automáticamente los detalles basados en la atención
                factura.generar_detalles()
                
                # Emitir la factura si se solicita
                if data.get("emitir", False):
                    factura.emitir()

                save_audit(request, factura, "A")
                messages.success(
                    request,
                    f"Éxito al crear la factura #{factura.numero_factura}"
                )
                return JsonResponse({
                    "msg": "Éxito al crear la factura.",
                    "id": factura.id,
                    "numero": factura.numero_factura
                }, status=200)
        except Exception as ex:
            messages.error(request, "Error al crear la factura")
            return JsonResponse({"msg": str(ex)}, status=400)
        
class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'attention/invoice/detail.html'
    context_object_name = 'factura'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura = self.get_object()
        
        # Agrupar detalles por tipo
        context['consultas'] = factura.detalles.filter(tipo='CONSULTA')
        context['medicamentos'] = factura.detalles.filter(tipo='MEDICAMENTO')
        context['examenes'] = factura.detalles.filter(tipo='EXAMEN')
        context['servicios'] = factura.detalles.filter(tipo='SERVICIO')
        
        # Datos del paciente desde la atención
        context['paciente'] = factura.atencion.paciente
        
        # Datos para PayPal
        if settings.PAYPAL_CLIENT_ID:
            context['paypal_client_id'] = settings.PAYPAL_CLIENT_ID
            
        return context

    def post(self, request, *args, **kwargs):
        factura = self.get_object()
        payment_method = request.POST.get('payment_method')
        
        if factura.estado != 'BORRADOR':
            return JsonResponse({
                'status': 'error',
                'message': 'Esta factura no está en estado borrador'
            }, status=400)

        if payment_method == 'cash':
            try:
                factura.estado = 'PAGADA'
                factura.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Pago en efectivo registrado exitosamente'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
                
        elif payment_method == 'paypal':
            try:
                payment = Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(
                            reverse('factura:payment_success')
                        ),
                        "cancel_url": request.build_absolute_uri(
                            reverse('factura:payment_cancel')
                        )
                    },
                    "transactions": [{
                        "amount": {
                            "total": str(factura.total),
                            "currency": "USD"
                        },
                        "description": f"Factura médica #{factura.numero_factura}"
                    }]
                })

                if payment.create():
                    # Guardar el payment_id en la sesión
                    request.session['paypal_payment_id'] = payment.id
                    request.session['factura_id'] = factura.id
                    
                    # Redireccionar a PayPal
                    for link in payment.links:
                        if link.method == "REDIRECT":
                            return JsonResponse({
                                'status': 'redirect',
                                'url': link.href
                            })
                            
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Error al crear el pago en PayPal'
                    }, status=400)
                    
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
        
        return JsonResponse({
            'status': 'error',
            'message': 'Método de pago no válido'
        }, status=400)

def payment_success(request):
    payment_id = request.session.get('paypal_payment_id')
    factura_id = request.session.get('factura_id')
    
    if payment_id and factura_id:
        payment = Payment.find(payment_id)
        if payment.execute({"payer_id": request.GET.get('PayerID')}):
            factura = Factura.objects.get(id=factura_id)
            factura.estado = 'PAGADA'
            factura.save()
            
            del request.session['paypal_payment_id']
            del request.session['factura_id']
            
            return redirect('attention:invoice_detail', pk=factura_id)
    
    return redirect('attention:invoice_payment_error')

def payment_cancel(request):
    return redirect('attention:invoice_detail', pk=request.session.get('factura_id'))