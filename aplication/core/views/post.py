from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit
from aplication.core.forms.post import CargoForm
from aplication.core.models import Cargo

class PostListView(LoginRequiredMixin, ListViewMixin, ListView):
    template_name = "core/post/list.html"
    model = Cargo
    context_object_name = 'cargos'

    def get_queryset(self):
        self.query = Q()
        q1 = self.request.GET.get('q')
        if q1 is not None:
            self.query.add(Q(nombre__icontains=q1), Q.OR)
            self.query.add(Q(descripcion__icontains=q1), Q.OR)
        return self.model.objects.filter(self.query).order_by('nombre')

class PostCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
    model = Cargo
    template_name = 'core/post/form.html'
    form_class = CargoForm
    success_url = reverse_lazy('core:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Grabar Cargo'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cargo = self.object
        save_audit(self.request, cargo, action='A')
        messages.success(self.request, f"Éxito al crear el cargo {cargo.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class PostUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
    model = Cargo
    template_name = 'core/post/form.html'
    form_class = CargoForm
    success_url = reverse_lazy('core:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Actualizar Cargo'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cargo = self.object
        save_audit(self.request, cargo, action='M')
        messages.success(self.request, f"Éxito al modificar el cargo {cargo.nombre}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Error al modificar el formulario. Corrige los errores.")
        return self.render_to_response(self.get_context_data(form=form))

class PostDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
    model = Cargo
    success_url = reverse_lazy('core:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['grabar'] = 'Eliminar Cargo'
        context['description'] = f"¿Desea eliminar el cargo: {self.object.nombre}?"
        context['back_url'] = self.success_url
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_message = f"Éxito al eliminar el cargo {self.object.nombre}."
        messages.success(self.request, success_message)
        return super().delete(request, *args, **kwargs)

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Cargo
    
    def get(self, request, *args, **kwargs):
        cargo = self.get_object()
        data = {
            'id': cargo.id,
            'nombre': cargo.nombre,
            'descripcion': cargo.descripcion,
            'activo': cargo.activo
        }
        return JsonResponse(data)