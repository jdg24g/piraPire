from rest_framework import serializers
from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    current_debt = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    available_credit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'name', 'type', 'initial_balance', 
            'current_balance', 'current_debt', 'credit_limit', 'available_credit',
            'statement_closing_day', 'payment_due_day', 'card_brand', 'issuer',
            'currency', 'is_active',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        wallet_type = data.get('type', getattr(self.instance, 'type', None))
        for field in ['statement_closing_day', 'payment_due_day']:
            value = data.get(field)
            if value is not None and (value < 1 or value > 31):
                raise serializers.ValidationError({field: "El día debe estar entre 1 y 31."})
        if wallet_type != 'CREDIT':
            data['credit_limit'] = None
            data['statement_closing_day'] = None
            data['payment_due_day'] = None
            data['card_brand'] = ''
            data['issuer'] = ''
        return data
