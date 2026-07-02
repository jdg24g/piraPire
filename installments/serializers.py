from rest_framework import serializers
from .models import InstallmentPurchase


class InstallmentPurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    pending_installments = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstallmentPurchase
        fields = [
            'id', 'user', 'wallet', 'wallet_name', 'category', 
            'category_name', 'product_name', 'total_amount', 
            'total_installments', 'installment_value', 
            'paid_installments', 'pending_installments', 
            'start_date', 'end_date', 'status', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['end_date']

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

        # Validar consistencia de cuotas
        total_installments = data.get('total_installments')
        paid_installments = data.get('paid_installments', 0)
        
        if total_installments is not None and total_installments <= 0:
            raise serializers.ValidationError({"total_installments": "La cantidad total de cuotas debe ser mayor a 0."})

        if total_installments is not None and paid_installments > total_installments:
            raise serializers.ValidationError({"paid_installments": "Las cuotas pagadas no pueden superar el total de cuotas."})

        return data
