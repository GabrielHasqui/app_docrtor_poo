from django.urls import reverse_lazy
from aplication.core.forms.doctor import DoctorForm
from aplication.core.models import Doctor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit

class DoctorListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/doctor/list.html"
    model = Doctor
    context_object_name = 'doctores'
    
    def get_queryset(self):
        query = Q()
        q1 = self.request.GET.get('q')
        if q1 is not None:
            query.add(Q(nombres__icontains=q1), Q.OR)
            query.add(Q(apellidos__icontains=q1), Q.OR)
            query.add(Q(cedula__icontains=q1), Q.OR)
        return self.model.objects.filter(query).order_by('apellidos')

class DoctorCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Doctor
    template_name = 'core/doctor/form.html'
    form_class = DoctorForm
    success_url = reverse_lazy('core:doctor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Doctor'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        doctor = self.object
        save_audit(self.request, doctor, action='A')
        messages.success(self.request, f"Éxito al crear al doctor {doctor.nombres} {doctor.apellidos}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class DoctorUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Doctor
    template_name = 'core/doctor/form.html'
    form_class = DoctorForm
    success_url = reverse_lazy('core:doctor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Doctor'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        doctor = self.object
        save_audit(self.request, doctor, action='M')
        messages.success(self.request, f"Éxito al modificar al doctor {doctor.nombres} {doctor.apellidos}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class DoctorDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = Doctor
    success_url = reverse_lazy('core:doctor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Doctor'
        context['description'] = f"¿Desea eliminar al doctor: {self.object.nombres} {self.object.apellidos}?"
        context['back_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar lógicamente al doctor {self.object.nombres} {self.object.apellidos}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor

    def get(self, request, *args, **kwargs):
        doctor = self.get_object()
        data = {
            'id': doctor.id,
            'nombres': doctor.nombres,
            'apellidos': doctor.apellidos,
            'foto': doctor.foto.url if doctor.foto else None,
            'fecha_nacimiento': doctor.fecha_nacimiento,
            'cedula': doctor.cedula,
            'direccion': doctor.direccion,
            'telefonos': doctor.telefonos,
            'email': doctor.email,
            'especialidades': [especialidad.nombre for especialidad in doctor.especialidad.all()],
            'horario_atencion': doctor.horario_atencion,
            'duracion_cita': doctor.duracion_cita,
            'activo': doctor.activo,
        }
        return JsonResponse(data)