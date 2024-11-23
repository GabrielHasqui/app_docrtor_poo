from django.urls import reverse_lazy
from aplication.core.forms.medicine import MedicineForm
from aplication.core.models import Medicamento
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit
from django.http import JsonResponse

class MedicineListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/medicine/list.html"
    model = Medicamento
    context_object_name = 'medicamentos'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.filter(nombre__icontains=query).order_by('nombre')
        return self.model.objects.all().order_by('nombre')

class MedicineCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Medicamento
    template_name = 'core/medicine/form.html'
    form_class = MedicineForm
    success_url = reverse_lazy('core:medicine_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medicine = self.object
        save_audit(self.request, medicine, action='A')
        messages.success(self.request, f"Éxito al crear el medicamento {medicine.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class MedicineUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Medicamento
    template_name = 'core/medicine/form.html'
    form_class = MedicineForm
    success_url = reverse_lazy('core:medicine_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        medicine = self.object
        save_audit(self.request, medicine, action='M')
        messages.success(self.request, f"Éxito al modificar el medicamento {medicine.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class MedicineDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = Medicamento
    success_url = reverse_lazy('core:medicine_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Medicamento'
        context['description'] = f"¿Desea eliminar el medicamento: {self.object.nombre}?"
        context['back_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar el medicamento {self.object.nombre}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)

class MedicineDetailView(LoginRequiredMixin, DetailView):
    model = Medicamento

    def get(self, request, *args, **kwargs):
        medicine = self.get_object()
        data = {
            'id': medicine.id,
            'nombre': medicine.nombre,
            'descripcion': medicine.descripcion,
            'concentracion': medicine.concentracion,
            'cantidad': medicine.cantidad,
            'precio': medicine.precio,
            'comercial': medicine.comercial,
            'activo': medicine.activo,
            'imagen': medicine.imagen.url if medicine.imagen else None,
            'tipo': medicine.tipo.nombre,
            'marca_medicamento': medicine.marca_medicamento.nombre if medicine.marca_medicamento else None,
        }
        return JsonResponse(data)