# ponytail: vistas web CRUD sencillas usando Class-Based Views de Django para billeteras
from decimal import Decimal, InvalidOperation

from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from transactions.models import Transaction
from .models import Wallet
from .forms import WalletForm
from .services import (
    create_balance_adjustment,
    get_wallet_auto_category,
    insufficient_balance_message,
    wallet_can_cover_expense,
)

class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'wallets/list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_source_wallets'] = Wallet.objects.filter(
            user=self.request.user,
            is_active=True,
        ).exclude(type='CREDIT')
        return context

class WalletCreateView(LoginRequiredMixin, CreateView):
    model = Wallet
    form_class = WalletForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        initial_balance = form.cleaned_data.get('initial_balance') or Decimal('0')
        form.instance.user = self.request.user
        if form.cleaned_data.get('type') == 'CREDIT':
            form.instance.initial_balance = 0
            messages.success(self.request, "Tarjeta de crédito creada exitosamente.")
            return super().form_valid(form)
        if initial_balance > 0:
            form.instance.initial_balance = 0
            with transaction.atomic():
                response = super().form_valid(form)
                Transaction.objects.create(
                    user=self.request.user,
                    wallet=self.object,
                    category=get_wallet_auto_category(self.request.user, 'Saldo inicial', 'INCOME'),
                    type='INCOME',
                    subtype='UNIQUE',
                    amount=initial_balance,
                    date=timezone.localdate(),
                    description=f"Saldo inicial - {self.object.name}",
                )
            messages.success(self.request, "Cuenta creada con ingreso inicial registrado.")
            return response
        messages.success(self.request, "Cuenta creada exitosamente.")
        return super().form_valid(form)

class WalletUpdateView(LoginRequiredMixin, UpdateView):
    model = Wallet
    form_class = WalletForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Cuenta actualizada exitosamente.")
        return super().form_valid(form)


class CreditCardPaymentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        credit_wallet = get_object_or_404(
            Wallet,
            pk=pk,
            user=request.user,
            type='CREDIT',
            is_active=True,
        )
        source_wallet = get_object_or_404(
            Wallet,
            pk=request.POST.get('source_wallet'),
            user=request.user,
            is_active=True,
        )
        if source_wallet.pk == credit_wallet.pk or source_wallet.type == 'CREDIT':
            messages.error(request, "Selecciona una cuenta origen que no sea tarjeta de crédito.")
            return redirect('wallet_list')

        try:
            amount = Decimal(request.POST.get('amount', ''))
        except (InvalidOperation, TypeError):
            amount = Decimal('0')
        if amount <= 0:
            messages.error(request, "El monto del pago debe ser mayor a cero.")
            return redirect('wallet_list')
        if not wallet_can_cover_expense(source_wallet, amount):
            messages.error(request, insufficient_balance_message(source_wallet, amount))
            return redirect('wallet_list')

        category = get_wallet_auto_category(request.user, 'Pago de tarjeta')
        with transaction.atomic():
            Transaction.objects.create(
                user=request.user,
                wallet=source_wallet,
                category=category,
                type='EXPENSE',
                subtype='CREDIT_PAYMENT',
                amount=amount,
                date=timezone.localdate(),
                description=f"Pago de tarjeta - {credit_wallet.name}",
            )
            Transaction.objects.create(
                user=request.user,
                wallet=credit_wallet,
                category=category,
                type='INCOME',
                subtype='CREDIT_PAYMENT',
                amount=amount,
                date=timezone.localdate(),
                description=f"Pago recibido desde {source_wallet.name}",
            )

        messages.success(request, "Pago de tarjeta registrado exitosamente.")
        return redirect('wallet_list')


class WalletBalanceAdjustView(LoginRequiredMixin, View):
    def post(self, request, pk):
        wallet = get_object_or_404(
            Wallet,
            pk=pk,
            user=request.user,
            is_active=True,
        )

        try:
            tx, difference = create_balance_adjustment(
                request.user,
                wallet,
                request.POST.get('target_balance'),
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect('wallet_list')

        if tx is None:
            messages.info(request, "El saldo ya coincide con el saldo real indicado.")
        elif difference > 0:
            messages.success(request, f"Saldo ajustado con un ingreso de {difference}.")
        else:
            messages.success(request, f"Saldo ajustado con un gasto de {abs(difference)}.")
        return redirect('wallet_list')
