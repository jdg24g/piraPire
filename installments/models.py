import datetime
from django.db import models
from django.conf import settings
from wallets.models import Wallet
from categories.models import Category


def add_months(sourcedate, months):
    # ponytail: suma meses de forma nativa sin dependencias externas
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    # Manejar días fuera de rango para meses más cortos
    days_in_month = [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]
    day = min(sourcedate.day, days_in_month[month - 1])
    return datetime.date(year, month, day)


class InstallmentPurchase(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Activa'),
        ('COMPLETED', 'Completada'),
        ('CANCELED', 'Cancelada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='installments'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='installments'
    )
    product_name = models.CharField(max_length=150)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_installments = models.PositiveIntegerField()
    installment_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    paid_installments = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.product_name} - {self.paid_installments}/{self.total_installments} - {self.user.username}"

    @property
    def pending_installments(self):
        return max(0, self.total_installments - self.paid_installments)

    @property
    def paid_percentage(self):
        if self.total_installments > 0:
            return min(100, int((self.paid_installments / self.total_installments) * 100))
        return 0

    def save(self, *args, **kwargs):
        # ponytail: calcular automáticamente el valor de cada cuota y la fecha de finalización
        if not self.installment_value and self.total_installments > 0:
            self.installment_value = self.total_amount / self.total_installments
        
        if self.start_date and self.total_installments > 0:
            # Las cuotas duran N-1 meses a partir del mes de inicio
            self.end_date = add_months(self.start_date, self.total_installments - 1)

        # Si se pagaron todas las cuotas, marcar como completada
        if self.paid_installments >= self.total_installments:
            self.status = 'COMPLETED'

        super().save(*args, **kwargs)
