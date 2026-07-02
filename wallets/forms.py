# ponytail: formulario simple para Wallet
from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name', 'type', 'initial_balance', 'currency', 'is_active']
        labels = {
            'name': 'Nombre de la Cuenta',
            'type': 'Tipo de Cuenta',
            'initial_balance': 'Saldo Inicial',
            'currency': 'Moneda',
            'is_active': 'Activa',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-slate-800 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-purple-500'}),
            'initial_balance': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 backdrop-blur-md'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded bg-white/10 border-white/20 text-purple-600 focus:ring-purple-500 h-5 w-5'}),
        }
