from rest_framework import serializers
from .models import RecurrentMovement


class RecurrentMovementSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = RecurrentMovement
        fields = [
            'id', 'user', 'wallet', 'wallet_name', 'category', 
            'category_name', 'type', 'amount', 'start_date', 
            'end_date', 'frequency', 'description', 'is_active', 
            'created_at', 'updated_at'
        ]

    def validate_amount(self, value):
        if value <= 0:
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
