from django.urls import path
from .views import (
    DashboardView,
    CategoryReportView,
    WalletReportView,
    MonthlyComparisonReportView,
    YearlyComparisonReportView,
    SummaryReportView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='reports_dashboard'),
    path('by-category/', CategoryReportView.as_view(), name='reports_by_category'),
    path('by-wallet/', WalletReportView.as_view(), name='reports_by_wallet'),
    path('monthly-comparison/', MonthlyComparisonReportView.as_view(), name='reports_monthly_comparison'),
    path('yearly-comparison/', YearlyComparisonReportView.as_view(), name='reports_yearly_comparison'),
    path('summary/', SummaryReportView.as_view(), name='reports_summary'),
]
