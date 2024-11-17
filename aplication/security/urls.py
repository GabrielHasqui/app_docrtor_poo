from django.urls import path
from aplication.security.views.user import AdminDashboardView

app_name = 'security'

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]
