from rest_framework import serializers
from .models import InstallmentPurchase


class InstallmentPurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    pending_installments = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    installment_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

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
        instance = self.instance
        total_installments = data.get('total_installments', getattr(instance, 'total_installments', None))
        paid_installments = data.get('paid_installments', getattr(instance, 'paid_installments', 0)) or 0
        total_amount = data.get('total_amount', getattr(instance, 'total_amount', None))
        installment_value = data.get('installment_value', getattr(instance, 'installment_value', None))
        
        if total_installments is not None and total_installments <= 0:
            raise serializers.ValidationError({"total_installments": "La cantidad total de cuotas debe ser mayor a 0."})

        if total_installments is not None and paid_installments > total_installments:
            raise serializers.ValidationError({"paid_installments": "Las cuotas pagadas no pueden superar el total de cuotas."})

        if total_installments and total_amount is None and installment_value is None:
            raise serializers.ValidationError({
                "non_field_errors": "Debes proporcionar el Monto Total o el Valor de Cuota junto con la Cantidad de Cuotas."
            })

        if total_amount is not None and total_amount <= 0:
            raise serializers.ValidationError({"total_amount": "El Monto Total debe ser mayor a 0."})

        if installment_value is not None and installment_value <= 0:
            raise serializers.ValidationError({"installment_value": "El Valor de Cuota debe ser mayor a 0."})

        if total_installments and total_amount is None:
            data['total_amount'] = installment_value * total_installments
        elif total_installments and installment_value is None:
            data['installment_value'] = total_amount / total_installments

        return data
