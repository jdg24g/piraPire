# ponytail: vistas web CRUD para movimientos (Transactions) con filtrado y paso de usuario al form
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.db.models import Q
from .models import Transaction
from .forms import TransactionForm
from wallets.models import Wallet
from wallets.services import transaction_delete_keeps_wallet_non_negative
from categories.models import Category

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        
        # Filtros
        self.date_from = self.request.GET.get('date_from')
        self.date_to = self.request.GET.get('date_to')
        self.type_filter = self.request.GET.get('type')
        self.wallet_filter = self.request.GET.get('wallet')
        self.category_filter = self.request.GET.get('category')

        if self.date_from:
            qs = qs.filter(date__gte=self.date_from)
        if self.date_to:
            qs = qs.filter(date__lte=self.date_to)
        if self.type_filter:
            qs = qs.filter(type=self.type_filter)
        if self.wallet_filter:
            qs = qs.filter(wallet_id=self.wallet_filter)
        if self.category_filter:
            qs = qs.filter(category_id=self.category_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(user=self.request.user)
        context['categories'] = Category.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        
        # Mantener los filtros en la paginación y vista
        context['filters'] = {
            'date_from': self.date_from or '',
            'date_to': self.date_to or '',
            'type': self.type_filter or '',
            'wallet': self.wallet_filter or '',
            'category': self.category_filter or '',
        }
        return context

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        tx_type = self.request.GET.get('type')
        if tx_type in ['INCOME', 'EXPENSE']:
            initial['type'] = tx_type
            initial['subtype'] = 'UNIQUE' if tx_type == 'INCOME' else 'NORMAL'
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Movimiento registrado exitosamente.")
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Movimiento actualizado exitosamente.")
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
        is_valid, message = transaction_delete_keeps_wallet_non_negative(transaction)
        if not is_valid:
            messages.error(request, message)
            next_url = request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('transaction_list')

        if hasattr(transaction, 'recurrence_payment'):
            transaction.recurrence_payment.delete()

        transaction.delete()
        messages.success(request, "Movimiento eliminado exitosamente.")
        next_url = request.POST.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('transaction_list')
