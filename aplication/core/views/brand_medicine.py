from django.urls import reverse_lazy
from aplication.core.forms.brand_medicine import BrandMedicineForm
from aplication.core.models import MarcaMedicamento
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin,PermissionMixin
from doctor.utils import save_audit
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.db.models import Q

class BrandMedicineListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/brand_medicine/list.html"
    model = MarcaMedicamento
    context_object_name = 'brand_medicines'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return MarcaMedicamento.objects.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            )
        return MarcaMedicamento.objects.all()
    
class BrandMedicineCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = MarcaMedicamento
    template_name = 'core/brand_medicine/form.html'
    form_class = BrandMedicineForm
    success_url = reverse_lazy('core:brand_medicine_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Marca de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        brand_medicine = self.object
        save_audit(self.request, brand_medicine, action='A')
        messages.success(self.request, f"Éxito al crear la marca de medicamento {brand_medicine.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class BrandMedicineUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = MarcaMedicamento
    template_name = 'core/brand_medicine/form.html'
    form_class = BrandMedicineForm
    success_url = reverse_lazy('core:brand_medicine_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Marca de Medicamento'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        brand_medicine = self.object
        save_audit(self.request, brand_medicine, action='M')
        messages.success(self.request, f"Éxito al modificar la marca de medicamento {brand_medicine.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class BrandMedicineDeleteView(DeleteView, DeleteViewMixin, LoginRequiredMixin):
    model = MarcaMedicamento
    template_name = 'core/brand_medicine/delete.html'
    success_url = reverse_lazy('core:brand_medicine_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Marca de medicamento eliminada con éxito.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, "Esta marca de medicamento no se puede eliminar porque está en uso en uno o más medicamentos.")
            return redirect(self.success_url)

class BrandMedicineDetailView(LoginRequiredMixin, DetailView):
    model = MarcaMedicamento

    def get(self, request, *args, **kwargs):
        brand_medicine = self.get_object()
        data = {
            'id': brand_medicine.id,
            'nombre': brand_medicine.nombre,
            'descripcion': brand_medicine.descripcion,
            'activo': brand_medicine.activo,
        }
        return JsonResponse(data)