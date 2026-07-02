from django.db import models
from django.conf import settings
from wallets.models import Wallet
from categories.models import Category


class RecurrentMovement(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Gasto'),
    ]

    FREQUENCY_CHOICES = [
        ('DAILY', 'Diaria'),
        ('WEEKLY', 'Semanal'),
        ('BIWEEKLY', 'Quincenal'),
        ('MONTHLY', 'Mensual'),
        ('YEARLY', 'Anual'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recurrences'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='recurrences'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='recurrences'
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, default='MONTHLY')
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.type} Recurrente ({self.get_frequency_display()}) - {self.amount} - {self.user.username}"
