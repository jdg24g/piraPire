from django.contrib import admin
from .models import RecurrentMovement, RecurrentPayment


@admin.register(RecurrentMovement)
class RecurrentMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'category', 'type', 'amount', 'amount_is_variable', 'frequency', 'due_day', 'start_date', 'is_active')
    list_filter = ('type', 'frequency', 'amount_is_variable', 'is_active', 'start_date')
    search_fields = ('description', 'user__username', 'category__name', 'wallet__name')
    ordering = ('-start_date',)


@admin.register(RecurrentPayment)
class RecurrentPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'recurrence', 'period_year', 'period_month', 'transaction', 'paid_at')
    list_filter = ('period_year', 'period_month')
    search_fields = ('recurrence__description', 'transaction__description')
