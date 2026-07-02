from django.contrib import admin
from .models import InstallmentPurchase


@admin.register(InstallmentPurchase)
class InstallmentPurchaseAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'user', 'wallet', 'category', 'total_amount', 'total_installments', 'paid_installments', 'status', 'start_date')
    list_filter = ('status', 'start_date', 'wallet')
    search_fields = ('product_name', 'user__username', 'category__name')
    ordering = ('-start_date',)
