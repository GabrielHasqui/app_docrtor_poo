from django.urls import reverse_lazy
from aplication.attention.forms.serviciosAdicionales import ServiciosAdicionalesForm 
from aplication.attention.models import ServiciosAdicionales
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from doctor.utils import save_audit

class ServiciosAdicionalesListView(LoginRequiredMixin,ListViewMixin,ListView):
   template_name = "attention/serviciosAdicionales/list.html"
   model = ServiciosAdicionales
   context_object_name = 'servicios'
   query = None
   paginate_by = 10
    
   def get_queryset(self):
      self.query = Q()
      q1 = self.request.GET.get('q') # ver
      status = self.request.GET.get('status')
        
      if q1 is not None: 
         self.query.add(Q(nombre_servicio__icontains=q1), Q.AND)   
            
      if status == "activo":
            self.query.add(Q(activo=True), Q.AND)
      elif status == "inactivo":
            self.query.add(Q(activo=False), Q.AND)
      return self.model.objects.filter(self.query).order_by('activo')

    
    
class ServiciosAdicionalesCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = ServiciosAdicionales
    template_name = 'attention/serviciosAdicionales/form.html'
    form_class = ServiciosAdicionalesForm
    success_url = reverse_lazy('attention:servicio_list')
    # permission_required = 'add_supplier' # en PermissionMixn se verfica si un grupo tiene el permiso

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar servicio'
        context['back_url'] = self.success_url
        return context
    
    def form_valid(self, form):
        # print("entro al form_valid")
        response = super().form_valid(form)
        servicio = self.object
        save_audit(self.request, servicio, action='A')
        messages.success(self.request, f"Éxito al crear el servicio {servicio.nombre_servicio}.")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
    
class ServiciosAdicionalesUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = ServiciosAdicionales
    template_name = 'attention/serviciosAdicionales/form.html'
    form_class = ServiciosAdicionalesForm
    success_url = reverse_lazy('attention:servicio_list')
    # permission_required = 'change_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar servicio'
        context['back_url'] = self.success_url
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        servicio = self.object
        save_audit(self.request, servicio, action='M')
        messages.success(self.request, f"Éxito al Modificar el servicio {servicio.nombre_servicio}.")
        print("mande mensaje")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
    
class ServiciosAdicionalesDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = ServiciosAdicionales
    # template_name = 'core/patient/form.html'
    success_url = reverse_lazy('attention:servicio_list')
    # permission_required = 'delete_supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar servicio'
        context['description'] = f"¿Desea Eliminar el servicio: {self.object.name}?"
        context['back_url'] = self.success_url
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar lógicamente el servicio {self.object.name}."
        messages.success(self.request, success_message)
        # Cambiar el estado de eliminado lógico
        # self.object.deleted = True
        # self.object.save()
        return super().delete(request, *args, **kwargs)
    
class ServiciosAdicionalesDetailView(LoginRequiredMixin,DetailView):
    model = ServiciosAdicionales
    
    def get(self, request, *args, **kwargs):
        servicio = self.get_object()
        data = {
            'id': servicio.id,
            'nombre_servicio': servicio.nombre_servicio,
            'costo_servicio': servicio.costo_servicio,
            'descripcion': servicio.descripcion,
            # Añade más campos según tu modelo
        }
        return JsonResponse(data)