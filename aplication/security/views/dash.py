from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from aplication.security.mixins.mixins import ListViewMixin

class AdminDashboardView(LoginRequiredMixin, ListViewMixin, View):
    def get(self, request):
        return render(
            request, "security/admin/dashboard/dashboard.html", {"user": request.user}
        )