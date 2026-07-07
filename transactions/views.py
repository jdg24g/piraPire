from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer
from .filters import TransactionFilter
from wallets.services import transaction_delete_keeps_wallet_non_negative


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = TransactionFilter

    def get_queryset(self):
        # El usuario solo ve sus propias transacciones
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_valid, message = transaction_delete_keeps_wallet_non_negative(instance)
        if not is_valid:
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
