from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from aplication.core.forms.blood_type import BloodTypeForm
from aplication.core.models import TipoSangre
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit

class BloodTypeListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/blood_type/list.html"
    model = TipoSangre
    context_object_name = 'tipos_sangre'
    
    def get_queryset(self):
        query = Q()
        q1 = self.request.GET.get('q')
        if q1 is not None:
            query.add(Q(tipo__icontains=q1), Q.OR)
        return self.model.objects.filter(query).order_by('tipo')

class BloodTypeCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = TipoSangre
    template_name = 'core/blood_type/form.html'
    form_class = BloodTypeForm
    success_url = reverse_lazy('core:blood_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Tipo de Sangre'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        blood_type = self.object
        save_audit(self.request, blood_type, action='A')
        messages.success(self.request, f"Éxito al crear el tipo de sangre {blood_type.tipo}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class BloodTypeUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = TipoSangre
    template_name = 'core/blood_type/form.html'
    form_class = BloodTypeForm
    success_url = reverse_lazy('core:blood_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Tipo de Sangre'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        blood_type = self.object
        save_audit(self.request, blood_type, action='M')
        messages.success(self.request, f"Éxito al modificar el tipo de sangre {blood_type.tipo}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class BloodTypeDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = TipoSangre
    success_url = reverse_lazy('core:blood_type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Tipo de Sangre'
        context['description'] = f"¿Desea eliminar el tipo de sangre: {self.object.tipo}?"
        context['back_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar lógicamente el tipo de sangre {self.object.tipo}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)

class BloodTypeDetailView(LoginRequiredMixin, DetailView):
    model = TipoSangre

    def get(self, request, *args, **kwargs):
        blood_type = self.get_object()
        data = {
            'id': blood_type.id,
            'tipo': blood_type.tipo,
            'descripcion': blood_type.descripcion,
        }
        return JsonResponse(data)