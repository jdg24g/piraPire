# ponytail: vistas web CRUD para compras en cuotas (InstallmentPurchase)
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from transactions.models import Transaction
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

    def get_initial_mode(self):
        return self.request.POST.get('entry_type') or self.request.GET.get('type', 'cuotas')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_mode'] = self.get_initial_mode()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        if self.request.POST.get('entry_type') == 'fijo':
            messages.success(self.request, "Gasto fijo mensual registrado exitosamente.")
        else:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_mode'] = self.request.POST.get('entry_type') or self.request.GET.get('type', 'cuotas')
        return context

    def form_valid(self, form):
        messages.success(self.request, "Compra en cuotas actualizada exitosamente.")
        return super().form_valid(form)


class InstallmentPurchasePayView(LoginRequiredMixin, View):
    def post(self, request, pk):
        purchase = get_object_or_404(
            InstallmentPurchase,
            pk=pk,
            user=request.user,
        )

        if purchase.status == 'CANCELED':
            messages.error(request, "No se puede pagar una compra cancelada.")
            return redirect('installment_list')

        if purchase.paid_installments >= purchase.total_installments:
            messages.error(request, "Esta compra ya tiene todas las cuotas pagadas.")
            return redirect('installment_list')

        with transaction.atomic():
            purchase.paid_installments += 1
            purchase.save()
            Transaction.objects.create(
                user=request.user,
                wallet=purchase.wallet,
                category=purchase.category,
                type='EXPENSE',
                subtype='INSTALLMENT',
                amount=purchase.installment_value,
                date=timezone.localdate(),
                description=f"{purchase.product_name} - cuota {purchase.paid_installments}/{purchase.total_installments}",
            )

        messages.success(request, "Cuota pagada y movimiento registrado exitosamente.")
        return redirect('installment_list')
