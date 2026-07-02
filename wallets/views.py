from rest_framework import viewsets, permissions
from .models import Wallet
from .serializers import WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propias cuentas
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Forzar que el creador sea el usuario actual
        serializer.save(user=self.request.user)
