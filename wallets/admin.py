from django.contrib import admin
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'type', 'initial_balance', 'currency', 'is_active', 'created_at')
    list_filter = ('type', 'currency', 'is_active')
    search_fields = ('name', 'user__username')
    ordering = ('user', 'name')
