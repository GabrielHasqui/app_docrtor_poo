from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from aplication.security.views.forms import ModuloForm
from aplication.security.models import Module
from aplication.security.instance.menu_module import MenuModule
from aplication.security.mixins.mixins import CreateViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q

# -- MENU CLASS --#
class ModuloListView(ListViewMixin, ListView):
    template_name = 'security/modulo/list.html'
    model = Module
    context_object_name = "modulos"
    permission_required = "view_module"
    paginate_by = 13
    
    def get_queryset(self): 
        self.query = Q(is_active=True)
        q1 = self.request.GET.get('q')
        print()
        if q1 is not None:
            self.query.add(Q(name__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by("id")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permission_add'] = context['permissions'].get('add_module', '')
        context['create_url'] = reverse_lazy('security:modulo_create')
        return context

class ModuloCreateView(CreateViewMixin, CreateView):
    model = Module
    template_name = "security/modulo/form.html"
    form_class = ModuloForm
    permission_required = "add_module"
    success_url = reverse_lazy('security:modulo_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Grabar Modulo'
        context['back_url'] = self.success_url
        return context

class ModuloUpdateView(UpdateViewMixin, UpdateView):
    model = Module
    template_name = "security/modulo/form.html"
    form_class = ModuloForm
    permission_required = "change_module"
    success_url = reverse_lazy('security:modulo_list')
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar Modulo'
        context['back_url'] = self.success_url
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        modulo = self.object
        messages.success(self.request, f"Éxito al actualizar el Modulo {modulo.name}.")
        return response

class ModuloDeleteView(PermissionMixin, DeleteView):
    model = Module
    template_name = 'security/delete.html'
    success_url = reverse_lazy('security:modulo_list')
    permission_required = 'delete_module'

    def delete(self, request, *args, **kwargs):
        modulo = self.get_object()
        modulo.active = False  
        modulo.save()
        messages.success(request, f"Éxito al eliminar el Menú {modulo.name}.")
        return super().delete(request, *args, **kwargs)
