from django.urls import path
from aplication.security.views.dash import AdminDashboardView
from aplication.security.views import auth, menu, Modulos, GrupoModulos

app_name = 'security'

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
        #-- URLS DE CREDENCIALES (USER) --#
    path('auth/signup', auth.signup, name="auth_signup"),
    path('auth/login',auth.signin,name="auth_login"),
    path('auth/logout',auth.signout,name='auth_logout'),
    path('auth/profile_view',auth.profile_view,name='profile_view'),
    path("auth/update_profile", auth.update_profile, name="auth_profile"),
    # -- URLS DE MENUS --#
    path("menu_list/", menu.MenuListView.as_view(), name="menu_list"),
    path("menu_create/", menu.MenuCreateView.as_view(), name="menu_create"),
    path("menu_update/<int:pk>/", menu.MenuUpdateView.as_view(), name="menu_update"),
    path("menu_delete/<int:pk>/", menu.MenuDeleteView.as_view(), name="menu_delete"),
    # -- URLS DE MODULOS
    path("modulo_list/", Modulos.ModuloListView.as_view(), name="modulo_list"),
    path("modulo_create/", Modulos.ModuloCreateView.as_view(), name="modulo_create"),
    path("modulo_update/<int:pk>/", Modulos.ModuloUpdateView.as_view(), name="modulo_update"),
    path("modulo_delete/<int:pk>/", Modulos.ModuloDeleteView.as_view(), name="modulo_delete"),
    # -- URLS DE GRUPO MODULO PERMISOS --#
    path("GroupModulePermission_list/", GrupoModulos.GroupModulePermissionListView.as_view(), name="GroupModulePermission_list"),
    path("GroupModulePermission_create/", GrupoModulos.GroupModulePermissionCreateView.as_view(), name="GroupModulePermission_create"),
    path("GroupModulePermission_update/<int:pk>/", GrupoModulos.GroupModulePermissionUpdateView.as_view(),name="GroupModulePermission_update"),
    path("GroupModulePermission_delete/<int:pk>/", GrupoModulos.GroupModulePermissionDeleteView.as_view(), name="GroupModulePermission_delete"),
    
    path('module-permissions/', GrupoModulos.module_permissions_view, name='module_permissions_view'),
]
