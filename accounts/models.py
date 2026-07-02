from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # ponytail: modelo de usuario limpio y directo, listo para extender si es necesario.
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username
