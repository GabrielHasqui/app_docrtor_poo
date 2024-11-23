from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, models
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from aplication.attention.forms.examination_form import ExamenForm
from aplication.attention.models import DetalleExamen, Examen
from doctor.mixins import CreateViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit, custom_serializer
import json

class ExaminationListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "attention/examination/list.html"
    model = Examen
    context_object_name = "examenes"

    # def get_queryset(self):
    #     query = self.request.GET.get("q")
    #     if query:
    #         return self.model.objects.filter(tipo_examen__icontains(query).order_by("tipo_examen"))
    #     return self.model.objects.all().order_by("tipo_examen")

class ExaminationCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Examen
    form_class = ExamenForm
    template_name = "attention/examination/form.html"
    success_url = reverse_lazy("attention:examination_list")

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
                messages.success(request, f"Éxito al registrar el examen {examen.tipo_examen}")
                return JsonResponse({"msg": "Éxito al registrar el examen."}, status=200)
        except Exception as ex:
            messages.error(request, "Error al registrar el examen")
            return JsonResponse({"msg": str(ex)}, status=400)

class ExaminationUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Examen
    form_class = ExamenForm
    template_name = "attention/examination/form.html"
    success_url = reverse_lazy("attention:examination_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar'
        context['back_url'] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            with transaction.atomic():
                examen = self.get_object()
                examen.tipo_examen = data["tipo_examen"]
                examen.descripcion = data["descripcion"]
                examen.precio = data["precio"]
                examen.save()
                save_audit(request, examen, "M")
                messages.success(request, f"Éxito al actualizar el examen {examen.tipo_examen}")
                return JsonResponse({"msg": "Éxito al actualizar el examen."}, status=200)
        except Exception as ex:
            messages.error(request, "Error al actualizar el examen")
            return JsonResponse({"msg": str(ex)}, status=400)

class ExaminationDetailView(LoginRequiredMixin, DetailView):
    model = Examen
    template_name = "attention/examination/detail.html"
    context_object_name = "examen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen = self.get_object()
        detail_examenes = list(
            DetalleExamen.objects.filter(examen_id=examen.id, activo=True).values(
                "atencion_id", "atencion__paciente__nombre_completo", "resultado", "fecha_realizacion"
            )
        )
        context["detalle_examenes"] = json.dumps(detail_examenes, default=custom_serializer)
        return context

class ExaminationDeleteView(LoginRequiredMixin, DeleteView):
    model = Examen
    template_name = "attention/examination/delete.html"
    success_url = reverse_lazy("attention:examination_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Examen eliminado con éxito.")
            return JsonResponse({"msg": "Examen eliminado con éxito."}, status=200)
        except models.ProtectedError:
            messages.error(request, "Este examen no se puede eliminar porque está en uso.")
            return JsonResponse({"msg": "Este examen no se puede eliminar porque está en uso."}, status=400)
