from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'applies_to', 'user', 'is_default', 'is_active')
    list_filter = ('applies_to', 'is_default', 'is_active')
    search_fields = ('name', 'user__username', 'parent__name')
    ordering = ('is_default', 'name')
