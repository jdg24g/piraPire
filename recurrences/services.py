import calendar
from datetime import date

from django.utils import timezone

from .models import RecurrentPayment


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


def period_label(year, month):
    return f"{MONTH_NAMES[month].capitalize()} {year}"


def is_period_paid(recurrence, year, month):
    return RecurrentPayment.objects.filter(
        recurrence=recurrence,
        period_year=year,
        period_month=month,
    ).exists()


def build_period_status(recurrence, year, month, today=None):
    today = today or timezone.localdate()
    due_date = clamp_date(year, month, recurrence.due_day)
    paid = is_period_paid(recurrence, year, month)
    return {
        'year': year,
        'month': month,
        'label': period_label(year, month),
        'due_date': due_date,
        'is_paid': paid,
        'is_overdue': not paid and due_date < today,
        'status': 'PAID' if paid else 'OVERDUE' if due_date < today else 'PENDING',
    }


def get_current_period_status(recurrence, today=None):
    today = today or timezone.localdate()
    year = max(today.year, recurrence.start_date.year)
    month = today.month if year == today.year else recurrence.start_date.month

    if recurrence.start_date.year == year and recurrence.start_date.month > month:
        month = recurrence.start_date.month

    return build_period_status(recurrence, year, month, today=today)


def get_next_pending_period(recurrence, today=None, max_months=240):
    today = today or timezone.localdate()
    year = max(today.year, recurrence.start_date.year)
    month = today.month if year == today.year else recurrence.start_date.month

    if recurrence.start_date.year == year and recurrence.start_date.month > month:
        month = recurrence.start_date.month

    for _ in range(max_months):
        period = build_period_status(recurrence, year, month, today=today)
        if not period['is_paid']:
            return period
        year, month = add_period_month(year, month)

    return build_period_status(recurrence, year, month, today=today)


def get_latest_paid_period(recurrence):
    payment = RecurrentPayment.objects.filter(recurrence=recurrence).order_by(
        '-period_year',
        '-period_month',
    ).first()
    if not payment:
        return None

    return {
        'year': payment.period_year,
        'month': payment.period_month,
        'label': period_label(payment.period_year, payment.period_month),
        'paid_at': payment.paid_at,
        'transaction_id': payment.transaction_id,
    }
