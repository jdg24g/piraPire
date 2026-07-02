from django.urls import path
from .views import ExportTransactionsCSVView

urlpatterns = [
    path('transactions/csv/', ExportTransactionsCSVView.as_view(), name='export_transactions_csv'),
]
