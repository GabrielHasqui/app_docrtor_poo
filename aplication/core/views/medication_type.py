from django.urls import reverse_lazy
from aplication.core.forms.medication_type import MedicationTypeForm
from aplication.core.forms.medication_type import MedicationTypeForm
from aplication.core.models import TipoMedicamento
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect

class MedicationTypeListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/medication_type/list.html"
    model = TipoMedicamento
    context_object_name = 'medication_types'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.filter(nombre__icontains=query).order_by('nombre')
        return self.model.objects.all().order_by('nombre')

class MedicationTypeCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = TipoMedicamento
    template_name = 'core/medication_type/form.html'
    form_class = MedicationTypeForm
    success_url = reverse_lazy('core:medication_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Tipo de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medication_type = self.object
        save_audit(self.request, medication_type, action='A')
        messages.success(self.request, f"Éxito al crear el tipo de medicamento {medication_type.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class MedicationTypeUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = TipoMedicamento
    template_name = 'core/medication_type/form.html'
    form_class = MedicationTypeForm
    success_url = reverse_lazy('core:medication_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Tipo de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medication_type = self.object
        save_audit(self.request, medication_type, action='M')
        messages.success(self.request, f"Éxito al modificar el tipo de medicamento {medication_type.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class MedicationTypeDeleteView(DeleteView , DeleteViewMixin, LoginRequiredMixin):
    model = TipoMedicamento
    template_name = 'core/medication_type/delete.html'
    success_url = reverse_lazy('core:medication_type_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Tipo de medicamento eliminado con éxito.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, "Este tipo de medicamento no se puede eliminar porque está en uso en uno o más medicamentos.")
            return redirect(self.success_url)

class MedicationTypeDetailView(LoginRequiredMixin, DetailView):
    model = TipoMedicamento

    def get(self, request, *args, **kwargs):
        medication_type = self.get_object()
        data = {
            'id': medication_type.id,
            'nombre': medication_type.nombre,
            'descripcion': medication_type.descripcion,
            'activo': medication_type.activo,
        }
        return JsonResponse(data)