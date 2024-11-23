from django.db.models import Q 
from aplication.security.instance.group_permission import GroupPermission 
from aplication.security.instance.menu_module import MenuModule
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator


class ListViewMixin(object):
    query = None
    paginate_by = 2
    
    def dispatch(self, request, *args, **kwargs):
        self.query = Q()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
      
        context['permissions'] = self._get_permission_dict_of_group()
      
        MenuModule(self.request).fill(context)
        return context

    def _get_permission_dict_of_group(self):
        print(f"Request: {self.request}, User: {getattr(self.request, 'user', None)}")

        return GroupPermission.get_permission_dict_of_group(self.request.user)

class DetailViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self._get_permission_dict_of_group()
        MenuModule(self.request).fill(context)
        return context

    def _get_permission_dict_of_group(self):
        return GroupPermission.get_permission_dict_of_group(self.request.user)
    
class CreateViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self._get_permission_dict_of_group()
        MenuModule(self.request).fill(context)
        return context

    def _get_permission_dict_of_group(self):
        return GroupPermission.get_permission_dict_of_group(self.request.user)

class UpdateViewMixin(object):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self._get_permission_dict_of_group()
        MenuModule(self.request).fill(context)
        
        return context

    def _get_permission_dict_of_group(self):
        return GroupPermission.get_permission_dict_of_group(self.request.user)
    
class DeleteViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("entro al deleteMixin")
        context['permissions'] = self._get_permission_dict_of_group()
        MenuModule(self.request).fill(context)
        return context

    def _get_permission_dict_of_group(self):
        return GroupPermission.get_permission_dict_of_group(self.request.user)

class PermissionMixin:
    permission_required = ''

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            if not request:
                print("Error: el objeto request es None.")
                messages.error(request, "Error interno: request no inicializado.")
                return redirect('core:home')

            if not hasattr(request, 'session'):
                print("Error: el objeto request no tiene una sesión válida.")
                messages.error(request, "Error interno: sesión no encontrada.")
                return redirect('core:home')

            user = request.user
            print(f"Usuario actual: {user}")

            if 'group_id' not in request.session:
                self.set_group_session(request, user)

            if user.is_superuser:
                return super().get(request, *args, **kwargs)

            group = self.get_group_session(request)

            if not group:
                print("No se pudo obtener el grupo. Redirigiendo al home.")
                messages.error(request, "No tiene permisos para acceder a este módulo.")
                return redirect('core:home')

            permissions = self._get_permissions_to_validate()

            if not permissions:
                return super().get(request, *args, **kwargs)

            has_permission = group.groupmodulepermission_set.filter(
                module__permissions__codename__in=permissions
            ).exists()

            if not has_permission:
                print(f"El grupo {group.name} no tiene permisos para acceder a este módulo.")
                messages.error(request, "No tiene permisos para acceder a este módulo.")
                return redirect('core:home')

            return super().get(request, *args, **kwargs)

        except Exception as ex:
            print(f"Error inesperado al ingresar al módulo: {ex}")
            messages.error(request, f"Error inesperado al ingresar al módulo: {ex}")
            return redirect('core:dashboard')



    def set_group_session(self, request, user):
        groups = user.groups.all().order_by('id')
        if groups.exists():
            group = groups.first()
            request.session['group_id'] = group.id

    def get_group_session(self, request):
        group_id = request.session.get('group_id')
        if group_id:
            try:
                return Group.objects.get(pk=group_id)
            except Group.DoesNotExist:
                return None
        return None

    def _get_permissions_to_validate(self):
        if not self.permission_required:
            return ()
        if isinstance(self.permission_required, str):
            return self.permission_required,
        return tuple(self.permission_required)
