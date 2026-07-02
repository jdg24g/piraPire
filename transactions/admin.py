from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'category', 'type', 'subtype', 'amount', 'date')
    list_filter = ('type', 'subtype', 'date', 'wallet')
    search_fields = ('description', 'user__username', 'category__name', 'wallet__name')
    ordering = ('-date', '-created_at')
    date_hierarchy = 'date'
