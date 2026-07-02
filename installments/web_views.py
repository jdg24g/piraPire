import calendar
from datetime import date

# ponytail: vistas web CRUD para compras en cuotas (InstallmentPurchase)
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from recurrences.models import RecurrentMovement, RecurrentPayment
from transactions.models import Transaction
from .models import InstallmentPurchase
from .forms import InstallmentPurchaseForm


MONTH_NAMES = [
    '',
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
]


def add_period_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def clamp_date(year, month, day):
    return date(year, month, min(day, calendar.monthrange(year, month)[1]))


def get_next_pending_period(recurrence, today=None):
    today = today or timezone.localdate()
    year = max(today.year, recurrence.start_date.year)
    month = today.month if year == today.year else recurrence.start_date.month

    if recurrence.start_date.year == year and recurrence.start_date.month > month:
        month = recurrence.start_date.month

    for _ in range(240):
        paid = RecurrentPayment.objects.filter(
            recurrence=recurrence,
            period_year=year,
            period_month=month,
        ).exists()
        if not paid:
            due_date = clamp_date(year, month, recurrence.due_day)
            return {
                'year': year,
                'month': month,
                'label': f"{MONTH_NAMES[month].capitalize()} {year}",
                'due_date': due_date,
                'is_overdue': due_date < today,
            }
        year, month = add_period_month(year, month)

    due_date = clamp_date(year, month, recurrence.due_day)
    return {
        'year': year,
        'month': month,
        'label': f"{MONTH_NAMES[month].capitalize()} {year}",
        'due_date': due_date,
        'is_overdue': False,
    }

class InstallmentPurchaseListView(LoginRequiredMixin, ListView):
    model = InstallmentPurchase
    template_name = 'installments/list.html'
    context_object_name = 'installments'

    def get_queryset(self):
        return InstallmentPurchase.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixed_expenses = []
        qs = RecurrentMovement.objects.filter(
            user=self.request.user,
            type='EXPENSE',
            frequency='MONTHLY',
            is_active=True,
        ).select_related('wallet', 'category')

        for recurrence in qs:
            fixed_expenses.append({
                'recurrence': recurrence,
                'period': get_next_pending_period(recurrence),
            })

        context['fixed_expenses'] = fixed_expenses
        return context

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
        if self.request.POST.get('entry_type') == 'fijo':
            today = timezone.localdate()
            due_day = int(self.request.POST.get('due_day'))
            RecurrentMovement.objects.create(
                user=self.request.user,
                wallet=form.cleaned_data['wallet'],
                category=form.cleaned_data['category'],
                type='EXPENSE',
                amount=form.cleaned_data['installment_value'],
                start_date=clamp_date(today.year, today.month, due_day),
                due_day=due_day,
                frequency='MONTHLY',
                description=form.cleaned_data['product_name'],
                is_active=True,
            )
            messages.success(self.request, "Gasto fijo mensual registrado exitosamente.")
            return redirect('installment_list')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_mode'] = 'cuotas'
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


class FixedExpensePayView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recurrence = get_object_or_404(
            RecurrentMovement,
            pk=pk,
            user=request.user,
            type='EXPENSE',
            frequency='MONTHLY',
            is_active=True,
        )

        try:
            period_year = int(request.POST.get('period_year'))
            period_month = int(request.POST.get('period_month'))
        except (TypeError, ValueError):
            messages.error(request, "No se pudo identificar el mes a pagar.")
            return redirect('installment_list')

        if period_month < 1 or period_month > 12:
            messages.error(request, "El mes a pagar no es válido.")
            return redirect('installment_list')

        label = f"{MONTH_NAMES[period_month].capitalize()} {period_year}"
        if RecurrentPayment.objects.filter(
            recurrence=recurrence,
            period_year=period_year,
            period_month=period_month,
        ).exists():
            messages.error(request, f"{label} ya estaba marcado como pagado.")
            return redirect('installment_list')

        with transaction.atomic():
            tx = Transaction.objects.create(
                user=request.user,
                wallet=recurrence.wallet,
                category=recurrence.category,
                type='EXPENSE',
                subtype='FIXED',
                amount=recurrence.amount,
                date=timezone.localdate(),
                description=f"{recurrence.description} - pago {label}",
            )
            RecurrentPayment.objects.create(
                recurrence=recurrence,
                transaction=tx,
                period_year=period_year,
                period_month=period_month,
            )

        messages.success(request, f"Gasto fijo de {label} marcado como pagado.")
        return redirect('installment_list')


class FixedExpenseDeactivateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recurrence = get_object_or_404(
            RecurrentMovement,
            pk=pk,
            user=request.user,
            type='EXPENSE',
            frequency='MONTHLY',
        )
        recurrence.is_active = False
        recurrence.end_date = timezone.localdate()
        recurrence.save(update_fields=['is_active', 'end_date', 'updated_at'])
        messages.success(request, "Gasto fijo mensual desactivado.")
        return redirect('installment_list')
