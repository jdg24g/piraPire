# ponytail: formulario simple para Transaction con filtros para wallet y category
from django import forms
from django.db.models import Q
from .models import Transaction
from wallets.models import Wallet
from wallets.services import transaction_keeps_wallets_non_negative
from categories.models import Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'subtype', 'wallet', 'category', 'amount', 'date', 'description']
        labels = {
            'type': 'Tipo',
            'subtype': 'Subtipo',
            'wallet': 'Cuenta',
            'category': 'Categoría',
            'amount': 'Monto',
            'date': 'Fecha',
            'description': 'Descripción (Opcional)',
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500', 'id': 'id_type'}),
            'subtype': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'wallet': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar wallets del usuario y activas
            self.fields['wallet'].queryset = Wallet.objects.filter(user=user, is_active=True)
            # Filtrar categorías del usuario o predeterminadas del sistema y que estén activas
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_default=True)
            ).filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get('wallet')
        amount = cleaned_data.get('amount')
        tx_type = cleaned_data.get('type')

        if wallet and amount and tx_type:
            is_valid, message = transaction_keeps_wallets_non_negative(
                wallet,
                tx_type,
                amount,
                self.instance,
            )
            if not is_valid:
                raise forms.ValidationError(message)

        return cleaned_data
