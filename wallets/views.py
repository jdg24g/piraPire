from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from categories.models import Category
from transactions.models import Transaction
from .models import Wallet
from .serializers import WalletSerializer


def get_wallet_auto_category(user, name, applies_to='BOTH'):
    category, _ = Category.objects.get_or_create(
        user=user,
        name=name,
        parent=None,
        defaults={
            'applies_to': applies_to,
            'is_active': True,
        },
    )
    return category


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propias cuentas
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Forzar que el creador sea el usuario actual
        initial_balance = serializer.validated_data.get('initial_balance') or Decimal('0')
        if serializer.validated_data.get('type') == 'CREDIT':
            serializer.save(user=self.request.user, initial_balance=0)
            return
        if initial_balance > 0:
            with transaction.atomic():
                wallet = serializer.save(user=self.request.user, initial_balance=0)
                Transaction.objects.create(
                    user=self.request.user,
                    wallet=wallet,
                    category=get_wallet_auto_category(self.request.user, 'Saldo inicial', 'INCOME'),
                    type='INCOME',
                    subtype='UNIQUE',
                    amount=initial_balance,
                    date=timezone.localdate(),
                    description=f"Saldo inicial - {wallet.name}",
                )
            return
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='pay-credit-card')
    def pay_credit_card(self, request, pk=None):
        credit_wallet = self.get_object()
        if credit_wallet.type != 'CREDIT':
            return Response(
                {'detail': 'La cuenta seleccionada no es una tarjeta de crédito.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(str(request.data.get('amount', '')))
        except (InvalidOperation, TypeError, ValueError):
            amount = Decimal('0')
        if amount <= 0:
            return Response(
                {'amount': 'El monto del pago debe ser mayor a cero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_wallet = Wallet.objects.filter(
            pk=request.data.get('source_wallet'),
            user=request.user,
            is_active=True,
        ).first()
        if not source_wallet or source_wallet.type == 'CREDIT' or source_wallet.pk == credit_wallet.pk:
            return Response(
                {'source_wallet': 'Selecciona una cuenta origen que no sea tarjeta de crédito.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = get_wallet_auto_category(request.user, 'Pago de tarjeta')
        with transaction.atomic():
            source_tx = Transaction.objects.create(
                user=request.user,
                wallet=source_wallet,
                category=category,
                type='EXPENSE',
                subtype='CREDIT_PAYMENT',
                amount=amount,
                date=timezone.localdate(),
                description=f"Pago de tarjeta - {credit_wallet.name}",
            )
            credit_tx = Transaction.objects.create(
                user=request.user,
                wallet=credit_wallet,
                category=category,
                type='INCOME',
                subtype='CREDIT_PAYMENT',
                amount=amount,
                date=timezone.localdate(),
                description=f"Pago recibido desde {source_wallet.name}",
            )

        return Response({
            'detail': 'Pago de tarjeta registrado exitosamente.',
            'source_transaction_id': source_tx.id,
            'credit_transaction_id': credit_tx.id,
            'wallet': self.get_serializer(credit_wallet).data,
        }, status=status.HTTP_201_CREATED)
