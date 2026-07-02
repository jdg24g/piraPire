from django.db import models
from django.conf import settings


class Category(models.Model):
    APPLIES_TO_CHOICES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Gasto'),
        ('BOTH', 'Ambos'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_categories'
    )
    name = models.CharField(max_length=100)
    applies_to = models.CharField(max_length=10, choices=APPLIES_TO_CHOICES, default='BOTH')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        # Evitar nombres duplicados de categoría por usuario
        unique_together = ('user', 'name', 'parent')

    def __str__(self):
        prefix = "[Default] " if self.is_default else ""
        parent_str = f" ({self.parent.name})" if self.parent else ""
        return f"{prefix}{self.name}{parent_str} - {self.get_applies_to_display()}"
