from django.db import models
from django.conf import settings


class Wallet(models.Model):
    # Opciones de tipos de cuenta
    TYPE_CHOICES = [
        ('CASH', 'Efectivo'),
        ('BANK', 'Cuenta bancaria'),
        ('DEBIT', 'Tarjeta de débito'),
        ('CREDIT', 'Tarjeta de crédito'),
        ('E_WALLET', 'Billetera electrónica'),
        ('OTHER', 'Otro'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CASH')
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=10, default='PYG')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        # Evitar nombres duplicados de cuenta por usuario
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.user.username}"

    # ponytail: calcular saldo actual dinámicamente para evitar desincronizaciones de base de datos.
    @property
    def current_balance(self):
        # Evitamos imports circulares importando localmente
        from transactions.models import Transaction
        
        income = Transaction.objects.filter(
            wallet=self,
            type='INCOME'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            wallet=self,
            type='EXPENSE'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return self.initial_balance + income - expense
