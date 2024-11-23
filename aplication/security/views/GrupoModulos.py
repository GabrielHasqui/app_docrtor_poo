from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from aplication.security.views.forms import ModuloForm, GroupModulePermissionForm
from aplication.security.models import GroupModulePermission, Permission, Module
from aplication.security.instance.menu_module import MenuModule
from aplication.security.mixins.mixins import CreateViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

def module_permissions_view(request):
    module_id = request.GET.get('module_id')
    if module_id:
        try:
            module = Module.objects.get(id=module_id)
            permissions = module.permissions.all()
            permissions_data = [{'id': permission.id, 'name': permission.name} for permission in permissions]
            return JsonResponse(permissions_data, safe=False)
        except Module.DoesNotExist:
            return JsonResponse({'error': 'Module not found'}, status=404)
    else:
        return JsonResponse({'error': 'Module ID not provided'}, status=400)

# -- MENU CLASS --#
class GroupModulePermissionListView(ListViewMixin, ListView):
    template_name = 'security/GroupModulePermission/list.html'
    model = GroupModulePermission
    context_object_name = "group_module_permissions"
    permission_required = "view_groupmodulepermission"
    paginate_by = 20
    
    def get_queryset(self):
        q1 = self.request.GET.get('q')
        print()
        if q1 is not None:
            self.query.add(Q(group__name__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by("id")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permission_add'] = context['permissions'].get('add_groupmodulepermission', '')
        context['create_url'] = reverse_lazy('security:GroupModulePermission_create')
        return context

class GroupModulePermissionCreateView(CreateViewMixin, CreateView):
    model = GroupModulePermission
    template_name = "security/GroupModulePermission/form.html"
    form_class = GroupModulePermissionForm
    permission_required = "add_groupmodulepermission"
    success_url = reverse_lazy('security:GroupModulePermission_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Grabar group module permission'
        context['back_url'] = self.success_url
        return context

class GroupModulePermissionUpdateView(UpdateViewMixin, UpdateView):
    model = GroupModulePermission
    template_name = "security/GroupModulePermission/form.html"
    form_class = GroupModulePermissionForm
    permission_required = "change_groupmodulepermission"
    success_url = reverse_lazy('security:GroupModulePermission_list')
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar group module permission'
        context['back_url'] = self.success_url
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        groupmodule = self.object
        messages.success(self.request, f"Éxito al actualizar el Modulo {groupmodule.group}.")
        return response

class GroupModulePermissionDeleteView(PermissionMixin, DeleteView):
    model = GroupModulePermission
    template_name = 'security/delete.html'
    success_url = reverse_lazy('security:GroupModulePermission_list')
    permission_required = 'delete_groupmodulepermission'

    def delete(self, request, *args, **kwargs):
        groupmodulepermission = self.get_object()
        groupmodulepermission.active = False  
        groupmodulepermission.save()
        messages.success(request, f"Éxito al eliminar el Menú {groupmodulepermission.name}.")
        return super().delete(request, *args, **kwargs)
