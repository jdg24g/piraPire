from django.db import models
from django.conf import settings
from wallets.models import Wallet
from categories.models import Category


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Gasto'),
    ]

    SUBTYPE_CHOICES = [
        # Ingresos
        ('UNIQUE', 'Ingreso Único'),
        ('RECURRENT', 'Ingreso Recurrente'),
        ('VARIABLE', 'Ingreso Variable'),
        # Gastos
        ('NORMAL', 'Gasto Normal'),
        ('FIXED', 'Gasto Fijo'),
        ('VARIABLE_FIXED', 'Gasto Fijo Variable'),
        ('INSTALLMENT', 'Compra en Cuotas'),
        ('CREDIT_PAYMENT', 'Pago de Tarjeta'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.date}) - {self.user.username}"
