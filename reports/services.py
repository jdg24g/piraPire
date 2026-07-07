import calendar
from datetime import date
from django.db import models
from django.db.models import Sum, Count, Q
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from installments.models import InstallmentPurchase
from wallets.models import Wallet
from categories.models import Category


def get_dashboard_data(user, year=None, month=None):
    # ponytail: lógica modular de agregación de reportes
    
    # Valores por defecto para mes y año actual
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Rango de fechas del mes
    last_day = calendar.monthrange(year, month)[1]
    start_date_filter = date(year, month, 1)
    end_date_filter = date(year, month, last_day)

    # Transacciones del mes
    txs_month = Transaction.objects.filter(
        user=user,
        date__range=(start_date_filter, end_date_filter)
    )
    budget_txs_month = txs_month.exclude(subtype='CREDIT_PAYMENT')

    # 1. Total ingresos y gastos
    totals = budget_txs_month.aggregate(
        total_income=Sum('amount', filter=Q(type='INCOME')),
        total_expense=Sum('amount', filter=Q(type='EXPENSE'))
    )
    total_income = totals['total_income'] or 0
    total_expense = totals['total_expense'] or 0
    balance = total_income - total_expense

    # 2. Gastos fijos y variables
    subtotals = budget_txs_month.aggregate(
        fixed=Sum('amount', filter=Q(type='EXPENSE', subtype='FIXED')),
        variable_fixed=Sum('amount', filter=Q(type='EXPENSE', subtype='VARIABLE_FIXED'))
    )
    fixed_expenses = subtotals['fixed'] or 0
    variable_fixed_expenses = subtotals['variable_fixed'] or 0

    # 3. Gastos en cuotas para el mes solicitado
    # Sumar el valor de las cuotas activas que caen en este mes
    target_absolute_months = year * 12 + month
    installment_purchases = InstallmentPurchase.objects.filter(user=user).exclude(status='CANCELED')
    
    installment_expenses = 0
    for purchase in installment_purchases:
        if purchase.start_date and purchase.end_date:
            start_absolute = purchase.start_date.year * 12 + purchase.start_date.month
            end_absolute = purchase.end_date.year * 12 + purchase.end_date.month
            if start_absolute <= target_absolute_months <= end_absolute:
                installment_expenses += purchase.installment_value or 0

    # 4. Categoría con mayor gasto
    top_cat_query = txs_month.filter(type='EXPENSE')\
        .values('category__name')\
        .annotate(total=Sum('amount'))\
        .order_index = 0
    
    # Para evitar excepciones si no hay datos
    top_cat_list = list(budget_txs_month.filter(type='EXPENSE')
                        .values('category__name')
                        .annotate(total=models.Sum('amount'))
                        .order_by('-total')[:1])
    top_expense_category = top_cat_list[0]['category__name'] if top_cat_list else None

    # 5. Cuenta con mayor movimiento (ingresos + gastos)
    top_wallet_list = list(budget_txs_month.values('wallet__name')
                           .annotate(total=models.Sum('amount'))
                           .order_by('-total')[:1])
    top_wallet = top_wallet_list[0]['wallet__name'] if top_wallet_list else None

    # 6. Últimos movimientos (5 transacciones)
    # Se obtienen del total de transacciones del usuario, no solo del mes
    recent_transactions = list(
        Transaction.objects.filter(user=user)
        .values('id', 'type', 'subtype', 'amount', 'date', 'description', 'category__name', 'wallet__name')[:5]
    )

    # 7. Promedio diario de gasto
    # Si es el mes actual, dividimos por el día de hoy para un promedio más real, sino por total de días
    if year == today.year and month == today.month:
        days_to_divide = today.day
    else:
        days_to_divide = last_day
    daily_expense_average = total_expense / days_to_divide if days_to_divide > 0 else 0

    return {
        "period": f"{year}-{month:02d}",
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "balance": float(balance),
        "fixed_expenses": float(fixed_expenses),
        "variable_fixed_expenses": float(variable_fixed_expenses),
        "installment_expenses": float(installment_expenses),
        "top_expense_category": top_expense_category,
        "top_wallet": top_wallet,
        "recent_transactions": recent_transactions,
        "daily_expense_average": float(daily_expense_average)
    }


def get_reports_data(user, report_type, filters=None):
    if filters is None:
        filters = {}

    # Construir queryset base de transacciones del usuario
    qs = Transaction.objects.filter(user=user).exclude(subtype='CREDIT_PAYMENT')

    # Aplicar filtros
    date_from = filters.get('date_from')
    if date_from:
        qs = qs.filter(date__gte=date_from)
        
    date_to = filters.get('date_to')
    if date_to:
        qs = qs.filter(date__lte=date_to)

    wallet = filters.get('wallet')
    if wallet:
        qs = qs.filter(wallet_id=wallet)

    category = filters.get('category')
    if category:
        qs = qs.filter(category_id=category)

    tx_type = filters.get('type')
    if tx_type:
        qs = qs.filter(type=tx_type)

    subtype = filters.get('subtype')
    if subtype:
        qs = qs.filter(subtype=subtype)

    # Agregación según el reporte solicitado
    if report_type == 'by-category':
        # Agrupado por categoría
        data = qs.values('category__name', 'type')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')
        return list(data)

    elif report_type == 'by-wallet':
        # Agrupado por cuenta
        data = qs.values('wallet__name', 'type')\
            .annotate(total=Sum('amount'))\
            .order_by('-total')
        return list(data)

    elif report_type == 'monthly-comparison':
        # Agrupado por mes y año para comparación
        # Extraemos fecha usando truncamiento o funciones de base de datos simples
        # Dado que Django soporta extract de forma directa:
        data = qs.values('date__year', 'date__month', 'type')\
            .annotate(total=Sum('amount'))\
            .order_by('-date__year', '-date__month')
        return list(data)
        
    elif report_type == 'yearly-comparison':
        data = qs.values('date__year', 'type')\
            .annotate(total=Sum('amount'))\
            .order_by('-date__year')
        return list(data)

    # Reporte por defecto: resumen total del rango de fechas
    totals = qs.aggregate(
        total_income=Sum('amount', filter=Q(type='INCOME')),
        total_expense=Sum('amount', filter=Q(type='EXPENSE'))
    )
    return {
        "total_income": float(totals['total_income'] or 0),
        "total_expense": float(totals['total_expense'] or 0),
        "balance": float((totals['total_income'] or 0) - (totals['total_expense'] or 0)),
        "transactions_count": qs.count()
    }
