from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from transactions.models import Transaction
from .models import RecurrentMovement, RecurrentPayment
from .serializers import RecurrentMovementSerializer
from .services import get_next_pending_period, period_label


class RecurrentMovementViewSet(viewsets.ModelViewSet):
    serializer_class = RecurrentMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['wallet', 'category', 'type', 'frequency', 'is_active']

    def get_queryset(self):
        return RecurrentMovement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        recurrence = self.get_object()
        if recurrence.type != 'EXPENSE' or recurrence.frequency != 'MONTHLY':
            return Response(
                {'detail': 'Solo se pueden marcar pagos mensuales de gastos fijos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not recurrence.is_active:
            return Response(
                {'detail': 'No se puede pagar un gasto fijo desactivado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        next_period = get_next_pending_period(recurrence)
        try:
            period_year = int(request.data.get('period_year') or next_period['year'])
            period_month = int(request.data.get('period_month') or next_period['month'])
        except (TypeError, ValueError):
            return Response(
                {'detail': 'El período a pagar no es válido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if period_month < 1 or period_month > 12:
            return Response(
                {'detail': 'El mes a pagar debe estar entre 1 y 12.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        label = period_label(period_year, period_month)
        if RecurrentPayment.objects.filter(
            recurrence=recurrence,
            period_year=period_year,
            period_month=period_month,
        ).exists():
            return Response(
                {'detail': f'{label} ya está marcado como pagado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = recurrence.amount
        subtype = 'FIXED'
        if recurrence.amount_is_variable:
            try:
                amount = Decimal(str(request.data.get('amount', '')))
            except (InvalidOperation, TypeError, ValueError):
                amount = Decimal('0')
            if amount <= 0:
                return Response(
                    {'amount': 'Debes ingresar el monto pagado este mes.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subtype = 'VARIABLE_FIXED'

        with transaction.atomic():
            tx = Transaction.objects.create(
                user=request.user,
                wallet=recurrence.wallet,
                category=recurrence.category,
                type='EXPENSE',
                subtype=subtype,
                amount=amount,
                date=timezone.localdate(),
                description=f"{recurrence.description} - pago {label}",
            )
            payment = RecurrentPayment.objects.create(
                recurrence=recurrence,
                transaction=tx,
                period_year=period_year,
                period_month=period_month,
            )

        serializer = self.get_serializer(recurrence)
        return Response(
            {
                'detail': f'Gasto fijo de {label} marcado como pagado.',
                'payment': {
                    'id': payment.id,
                    'period_year': payment.period_year,
                    'period_month': payment.period_month,
                    'transaction_id': tx.id,
                },
                'recurrence': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
