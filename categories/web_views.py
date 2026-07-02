# ponytail: vistas web CRUD sencillas usando Class-Based Views de Django para categorías
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Category
from .forms import CategoryForm

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Mostrar categorías del usuario o las globales predeterminadas
        return Category.objects.filter(Q(user=self.request.user) | Q(is_default=True))

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('category_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Categoría creada exitosamente.")
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('category_list')

    def get_queryset(self):
        # Solo se permite editar las del usuario (no las predeterminadas del sistema)
        return Category.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada exitosamente.")
        return super().form_valid(form)
