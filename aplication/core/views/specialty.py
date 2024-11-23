from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from aplication.core.forms.specialty import SpecialtyForm
from aplication.core.models import Especialidad
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit

class SpecialtyListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/specialty/list.html"
    model = Especialidad
    context_object_name = 'especialidades'
    
    def get_queryset(self):
        query = Q()
        q1 = self.request.GET.get('q')
        if q1 is not None:
            query.add(Q(nombre__icontains=q1), Q.OR)
        return self.model.objects.filter(query).order_by('nombre')

class SpecialtyCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Especialidad
    template_name = 'core/specialty/form.html'
    form_class = SpecialtyForm
    success_url = reverse_lazy('core:specialty_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Especialidad'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        specialty = self.object
        save_audit(self.request, specialty, action='A')
        messages.success(self.request, f"Éxito al crear la especialidad {specialty.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class SpecialtyUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Especialidad
    template_name = 'core/specialty/form.html'
    form_class = SpecialtyForm
    success_url = reverse_lazy('core:specialty_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Especialidad'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        specialty = self.object
        save_audit(self.request, specialty, action='M')
        messages.success(self.request, f"Éxito al modificar la especialidad {specialty.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class SpecialtyDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = Especialidad
    success_url = reverse_lazy('core:specialty_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Especialidad'
        context['description'] = f"¿Desea eliminar la especialidad: {self.object.nombre}?"
        context['back_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar lógicamente la especialidad {self.object.nombre}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)

class SpecialtyDetailView(LoginRequiredMixin, DetailView):
    model = Especialidad

    def get(self, request, *args, **kwargs):
        specialty = self.get_object()
        data = {
            'id': specialty.id,
            'nombre': specialty.nombre,
            'descripcion': specialty.descripcion,
        }
        return JsonResponse(data)