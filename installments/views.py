from rest_framework import viewsets, permissions
from .models import InstallmentPurchase
from .serializers import InstallmentPurchaseSerializer


class InstallmentPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = InstallmentPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['wallet', 'category', 'status']

    def get_queryset(self):
        return InstallmentPurchase.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
