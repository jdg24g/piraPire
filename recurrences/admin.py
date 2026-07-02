from django.contrib import admin
from .models import RecurrentMovement


@admin.register(RecurrentMovement)
class RecurrentMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'category', 'type', 'amount', 'frequency', 'start_date', 'is_active')
    list_filter = ('type', 'frequency', 'is_active', 'start_date')
    search_fields = ('description', 'user__username', 'category__name', 'wallet__name')
    ordering = ('-start_date',)
