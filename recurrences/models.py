import calendar
from datetime import date
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
    due_day = models.PositiveSmallIntegerField(default=1)
    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES, default='MONTHLY')
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.type} Recurrente ({self.get_frequency_display()}) - {self.amount} - {self.user.username}"

    def due_date_for(self, year, month):
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, min(self.due_day, last_day))


class RecurrentPayment(models.Model):
    recurrence = models.ForeignKey(
        RecurrentMovement,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    transaction = models.OneToOneField(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recurrence_payment'
    )
    period_year = models.PositiveIntegerField()
    period_month = models.PositiveSmallIntegerField()
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_year', '-period_month']
        constraints = [
            models.UniqueConstraint(
                fields=['recurrence', 'period_year', 'period_month'],
                name='unique_recurrent_payment_period'
            )
        ]

    def __str__(self):
        return f"{self.recurrence_id} - {self.period_year}-{self.period_month:02d}"
