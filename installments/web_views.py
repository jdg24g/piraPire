import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

# ponytail: vistas web CRUD para compras en cuotas (InstallmentPurchase)
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from recurrences.models import RecurrentMovement, RecurrentPayment
from transactions.models import Transaction
from .models import InstallmentPurchase
from .forms import InstallmentPurchaseForm, FixedExpenseForm


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


def build_installment_sheet(user):
    rows = []
    totals = {
        'monthly_amount': Decimal('0'),
        'paid_count': 0,
        'total_installments': 0,
        'remaining_amount': Decimal('0'),
        'paid_amount': Decimal('0'),
        'total_amount': Decimal('0'),
        'remaining_count': 0,
    }

    purchases = InstallmentPurchase.objects.filter(user=user).select_related('wallet', 'category')
    for purchase in purchases:
        installment_value = purchase.installment_value or Decimal('0')
        total_amount = purchase.total_amount or (installment_value * purchase.total_installments)
        paid_amount = installment_value * purchase.paid_installments
        remaining_count = purchase.pending_installments
        remaining_amount = installment_value * remaining_count

        rows.append({
            'kind': 'installment',
            'label': purchase.product_name,
            'type_label': purchase.category.name,
            'wallet': purchase.wallet.name,
            'monthly_amount': installment_value,
            'paid_count': purchase.paid_installments,
            'total_installments': purchase.total_installments,
            'remaining_amount': remaining_amount,
            'paid_amount': paid_amount,
            'total_amount': total_amount,
            'remaining_count': remaining_count,
            'status': purchase.get_status_display(),
            'edit_url': reverse('installment_edit', args=[purchase.id]),
            'pay_url': reverse('installment_pay', args=[purchase.id]),
            'can_pay': purchase.status == 'ACTIVE' and remaining_count > 0,
        })

        totals['monthly_amount'] += installment_value
        totals['paid_count'] += purchase.paid_installments
        totals['total_installments'] += purchase.total_installments
        totals['remaining_amount'] += remaining_amount
        totals['paid_amount'] += paid_amount
        totals['total_amount'] += total_amount
        totals['remaining_count'] += remaining_count

    fixed_qs = RecurrentMovement.objects.filter(
        user=user,
        type='EXPENSE',
        frequency='MONTHLY',
        is_active=True,
    ).select_related('wallet', 'category')
    for recurrence in fixed_qs:
        period = get_next_pending_period(recurrence)
        monthly_amount = Decimal('0') if recurrence.amount_is_variable else recurrence.amount
        remaining_amount = monthly_amount

        rows.append({
            'kind': 'fixed',
            'label': recurrence.description,
            'type_label': recurrence.category.name,
            'wallet': recurrence.wallet.name,
            'monthly_amount': monthly_amount,
            'paid_count': 0,
            'total_installments': 1,
            'remaining_amount': remaining_amount,
            'paid_amount': Decimal('0'),
            'total_amount': monthly_amount,
            'remaining_count': 1,
            'status': f"Pendiente {period['label']}",
            'edit_url': reverse('fixed_expense_edit', args=[recurrence.id]),
            'pay_url': reverse('fixed_expense_pay', args=[recurrence.id]),
            'deactivate_url': reverse('fixed_expense_deactivate', args=[recurrence.id]),
            'can_pay': True,
            'amount_is_variable': recurrence.amount_is_variable,
            'period': period,
        })

        totals['monthly_amount'] += monthly_amount
        totals['total_installments'] += 1
        totals['remaining_amount'] += remaining_amount
        totals['total_amount'] += monthly_amount
        totals['remaining_count'] += 1

    return rows, totals

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


class InstallmentSheetView(LoginRequiredMixin, TemplateView):
    template_name = 'installments/sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows, totals = build_installment_sheet(self.request.user)
        context['sheet_rows'] = rows
        context['sheet_totals'] = totals
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
        entry_type = self.request.POST.get('entry_type')
        if entry_type in ['fijo', 'fijo_variable']:
            today = timezone.localdate()
            due_day = int(self.request.POST.get('due_day'))
            RecurrentMovement.objects.create(
                user=self.request.user,
                wallet=form.cleaned_data['wallet'],
                category=form.cleaned_data['category'],
                type='EXPENSE',
                amount=form.cleaned_data['installment_value'] if entry_type == 'fijo' else 0,
                amount_is_variable=entry_type == 'fijo_variable',
                start_date=clamp_date(today.year, today.month, due_day),
                due_day=due_day,
                frequency='MONTHLY',
                description=form.cleaned_data['product_name'],
                is_active=True,
            )
            if entry_type == 'fijo_variable':
                messages.success(self.request, "Gasto fijo mensual variable registrado exitosamente.")
            else:
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

        amount = recurrence.amount
        subtype = 'FIXED'
        if recurrence.amount_is_variable:
            try:
                amount = Decimal(request.POST.get('amount', ''))
            except (InvalidOperation, TypeError):
                amount = Decimal('0')
            if amount <= 0:
                messages.error(request, "Debes ingresar el monto pagado este mes.")
                return redirect('installment_list')
            subtype = 'VARIABLE_FIXED'

        with transaction.atomic():
            tx = Transaction.objects.create(
                user=request.user,
                wallet=recurrence.wallet,
                category=recurrence.category,
                type='EXPENSE',
                subtype=subtype,
                amount=amount,
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


class FixedExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurrentMovement
    form_class = FixedExpenseForm
    template_name = 'installments/fixed_form.html'
    success_url = reverse_lazy('installment_list')

    def get_queryset(self):
        return RecurrentMovement.objects.filter(
            user=self.request.user,
            type='EXPENSE',
            frequency='MONTHLY',
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Gasto fijo mensual actualizado exitosamente.")
        return super().form_valid(form)


class FixedExpenseDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        recurrence = get_object_or_404(
            RecurrentMovement,
            pk=pk,
            user=request.user,
            type='EXPENSE',
            frequency='MONTHLY',
        )
        recurrence.delete()
        messages.success(request, "Gasto fijo mensual eliminado.")
        return redirect('installment_list')
