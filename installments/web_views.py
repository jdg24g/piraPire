# ponytail: vistas web CRUD para compras en cuotas (InstallmentPurchase)
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import InstallmentPurchase
from .forms import InstallmentPurchaseForm

class InstallmentPurchaseListView(LoginRequiredMixin, ListView):
    model = InstallmentPurchase
    template_name = 'installments/list.html'
    context_object_name = 'installments'

    def get_queryset(self):
        return InstallmentPurchase.objects.filter(user=self.request.user)

class InstallmentPurchaseCreateView(LoginRequiredMixin, CreateView):
    model = InstallmentPurchase
    form_class = InstallmentPurchaseForm
    template_name = 'installments/form.html'
    success_url = reverse_lazy('installment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Compra en cuotas registrada exitosamente.")
        return super().form_valid(form)

class InstallmentPurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = InstallmentPurchase
    form_class = InstallmentPurchaseForm
    template_name = 'installments/form.html'
    success_url = reverse_lazy('installment_list')

    def get_queryset(self):
        return InstallmentPurchase.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Compra en cuotas actualizada exitosamente.")
        return super().form_valid(form)
