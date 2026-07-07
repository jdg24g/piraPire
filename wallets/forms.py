# ponytail: formulario simple para Wallet
from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name', 'type', 'initial_balance', 'credit_limit', 'statement_closing_day', 'payment_due_day', 'card_brand', 'issuer', 'currency', 'is_active']
        labels = {
            'name': 'Nombre de la Cuenta',
            'type': 'Tipo de Cuenta',
            'initial_balance': 'Saldo Inicial',
            'credit_limit': 'Línea de Crédito',
            'statement_closing_day': 'Día de Cierre',
            'payment_due_day': 'Día de Vencimiento',
            'card_brand': 'Marca de Tarjeta',
            'issuer': 'Emisor / Banco',
            'currency': 'Moneda',
            'is_active': 'Activa',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01', 'min': '0'}),
            'statement_closing_day': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'min': '1', 'max': '31'}),
            'payment_due_day': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'min': '1', 'max': '31'}),
            'card_brand': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'placeholder': 'Mastercard, Visa...'}),
            'issuer': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'placeholder': 'Ueno Bank, Banco...'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded bg-white/10 border-white/20 text-purple-600 focus:ring-purple-500 h-5 w-5'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        wallet_type = cleaned_data.get('type')
        for field in ['statement_closing_day', 'payment_due_day']:
            value = cleaned_data.get(field)
            if value is not None and (value < 1 or value > 31):
                self.add_error(field, "El día debe estar entre 1 y 31.")
        if wallet_type != 'CREDIT':
            cleaned_data['credit_limit'] = None
            cleaned_data['statement_closing_day'] = None
            cleaned_data['payment_due_day'] = None
            cleaned_data['card_brand'] = ''
            cleaned_data['issuer'] = ''
        return cleaned_data
