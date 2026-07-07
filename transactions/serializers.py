from rest_framework import serializers
from .models import Transaction
from wallets.models import Wallet
from wallets.services import transaction_keeps_wallets_non_negative
from categories.models import Category


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'wallet', 'wallet_name', 'category', 
            'category_name', 'type', 'subtype', 'amount', 
            'date', 'description', 'created_at', 'updated_at'
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

        # Validar consistencia entre type y subtype
        t_type = data.get('type', getattr(self.instance, 'type', None))
        subtype = data.get('subtype', getattr(self.instance, 'subtype', None))
        
        income_subtypes = ['UNIQUE', 'RECURRENT', 'VARIABLE', 'CREDIT_PAYMENT']
        expense_subtypes = ['NORMAL', 'FIXED', 'VARIABLE_FIXED', 'INSTALLMENT', 'CREDIT_PAYMENT']

        if t_type == 'INCOME' and subtype not in income_subtypes:
            raise serializers.ValidationError(
                {"subtype": f"Para un ingreso, el subtipo debe ser uno de: {', '.join(income_subtypes)}"}
            )
        elif t_type == 'EXPENSE' and subtype not in expense_subtypes:
            raise serializers.ValidationError(
                {"subtype": f"Para un gasto, el subtipo debe ser uno de: {', '.join(expense_subtypes)}"}
            )

        amount = data.get('amount', getattr(self.instance, 'amount', None))
        wallet = data.get('wallet', getattr(self.instance, 'wallet', None))
        if wallet and amount and t_type:
            is_valid, message = transaction_keeps_wallets_non_negative(
                wallet,
                t_type,
                amount,
                self.instance,
            )
            if not is_valid:
                raise serializers.ValidationError({"amount": message})

        return data
