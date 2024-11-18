from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Q
from aplication.attention.models import HorarioAtencion
from aplication.attention.forms.ScheduleAttention import ScheduleAttentionForm
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit

class ScheduleAttentionListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "attention/schedule_attention/list.html"
    model = HorarioAtencion
    context_object_name = 'schedule_attentions'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return HorarioAtencion.objects.filter(
                Q(dia_semana__icontains=query)
            )
        return HorarioAtencion.objects.all()

class ScheduleAttentionCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = HorarioAtencion
    template_name = 'attention/schedule_attention/form.html'
    form_class = ScheduleAttentionForm
    success_url = reverse_lazy('attention:schedule_attention_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Horario de Atención'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        schedule_attention = self.object
        save_audit(self.request, schedule_attention, action='A')
        messages.success(self.request, f"Éxito al crear el horario de atención para {schedule_attention.dia_semana}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class ScheduleAttentionUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = HorarioAtencion
    template_name = 'attention/schedule_attention/form.html'
    form_class = ScheduleAttentionForm
    success_url = reverse_lazy('attention:schedule_attention_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Horario de Atención'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        schedule_attention = self.object
        save_audit(self.request, schedule_attention, action='M')
        messages.success(self.request, f"Éxito al modificar el horario de atención para {schedule_attention.dia_semana}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class ScheduleAttentionDeleteView(DeleteView, DeleteViewMixin, LoginRequiredMixin):
    model = HorarioAtencion
    success_url = reverse_lazy('attention:schedule_attention_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Horario de atención eliminado con éxito.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(request, "Este horario de atención no se puede eliminar porque está en uso.")
            return redirect(self.success_url)

class ScheduleAttentionDetailView(LoginRequiredMixin, DetailView):
    model = HorarioAtencion

    def get(self, request, *args, **kwargs):
        schedule_attention = self.get_object()
        data = {
            'id': schedule_attention.id,
            'dia_semana': schedule_attention.dia_semana,
            'hora_inicio': schedule_attention.hora_inicio.strftime('%H:%M'),
            'hora_fin': schedule_attention.hora_fin.strftime('%H:%M'),
            'intervalo_desde': schedule_attention.intervalo_desde.strftime('%H:%M'),
            'intervalo_hasta': schedule_attention.intervalo_hasta.strftime('%H:%M'),
            'activo': schedule_attention.activo,
        }
        return JsonResponse(data)