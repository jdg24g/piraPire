from rest_framework import serializers
from .models import RecurrentMovement
from .services import get_current_period_status, get_latest_paid_period, get_next_pending_period


class RecurrentMovementSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_period = serializers.SerializerMethodField()
    current_period_is_paid = serializers.SerializerMethodField()
    current_period_status = serializers.SerializerMethodField()
    next_pending_period = serializers.SerializerMethodField()
    latest_paid_period = serializers.SerializerMethodField()

    class Meta:
        model = RecurrentMovement
        fields = [
            'id', 'user', 'wallet', 'wallet_name', 'category', 
            'category_name', 'type', 'amount', 'amount_is_variable', 'start_date',
            'end_date', 'due_day', 'frequency', 'description', 'is_active',
            'current_period', 'current_period_is_paid', 'current_period_status',
            'next_pending_period', 'latest_paid_period',
            'created_at', 'updated_at'
        ]

    def get_current_period(self, obj):
        if obj.frequency != 'MONTHLY':
            return None
        return get_current_period_status(obj)

    def get_current_period_is_paid(self, obj):
        period = self.get_current_period(obj)
        return period['is_paid'] if period else None

    def get_current_period_status(self, obj):
        period = self.get_current_period(obj)
        return period['status'] if period else None

    def get_next_pending_period(self, obj):
        if obj.frequency != 'MONTHLY':
            return None
        return get_next_pending_period(obj)

    def get_latest_paid_period(self, obj):
        if obj.frequency != 'MONTHLY':
            return None
        return get_latest_paid_period(obj)

    def validate_due_day(self, value):
        if value < 1 or value > 31:
            raise serializers.ValidationError("El día de vencimiento debe estar entre 1 y 31.")
        return value

    def validate_amount(self, value):
        amount_is_variable = self.initial_data.get('amount_is_variable') in [True, 'true', 'True', '1', 1]
        if value <= 0 and not amount_is_variable:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value

    def validate(self, data):
        user = self.context['request'].user

        # Validar que la cuenta pertenezca al usuario
        wallet = data.get('wallet')
        if wallet and wallet.user != user:
            raise serializers.ValidationError({"wallet": "La cuenta seleccionada no le pertenece."})

        # Validar que la categoría sea del usuario o predeterminada
        category = data.get('category')
        if category and not category.is_default and category.user != user:
            raise serializers.ValidationError({"category": "La categoría seleccionada no le pertenece."})

        # Validar consistencia de fechas
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "La fecha de finalización no puede ser anterior a la de inicio."})

        return data
