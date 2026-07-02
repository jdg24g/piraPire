from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retornar categorías predeterminadas del sistema O las personalizadas del usuario
        return Category.objects.filter(
            Q(is_default=True) | Q(user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_default=False)

    def perform_update(self, serializer):
        # No permitir modificar categorías predeterminadas del sistema
        instance = self.get_object()
        if instance.is_default:
            raise PermissionDenied("No se pueden modificar las categorías predeterminadas del sistema.")
        serializer.save()

    def perform_destroy(self, instance):
        # No permitir eliminar categorías predeterminadas del sistema
        if instance.is_default:
            raise PermissionDenied("No se pueden eliminar las categorías predeterminadas del sistema.")
        instance.delete()
