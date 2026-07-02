# ponytail: vistas web para Dashboard y Reportes utilizando los servicios de negocio ya existentes
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date
import json
from django.core.serializers.json import DjangoJSONEncoder
from .services import get_dashboard_data, get_reports_data
from wallets.models import Wallet
from categories.models import Category
from django.db.models import Q

class WebDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        today = date.today()
        # Obtener mes y año desde los parámetros de consulta o usar el mes y año actual
        try:
            year_val = request.GET.get('year')
            month_val = request.GET.get('month')
            year = int(year_val) if year_val else today.year
            month = int(month_val) if month_val else today.month
            if month < 1 or month > 12:
                month = today.month
        except ValueError:
            year = today.year
            month = today.month

        dashboard_data = get_dashboard_data(request.user, year, month)
        
        # Para pasar a los gráficos Chart.js, necesitamos los gastos agrupados por categoría en este mes.
        # Podemos obtenerlo llamando a get_reports_data para el mes actual
        filters = {
            'date_from': date(year, month, 1).isoformat(),
            'date_to': date(year, month, 28).isoformat()  # ponytail: aproximación rápida, o usar calendar
        }
        # En vez de aproximar, usemos el rango de fechas real usado en dashboard_data
        # get_dashboard_data ya calcula y tiene "period"
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        filters['date_to'] = date(year, month, last_day).isoformat()
        
        # Obtener gastos agrupados por categoría para el gráfico
        filters_expense = filters.copy()
        filters_expense['type'] = 'EXPENSE'
        category_expenses = get_reports_data(request.user, 'by-category', filters_expense)
        
        # Obtener ingresos vs gastos del mes
        summary_data = get_reports_data(request.user, 'summary', filters)

        context = {
            'data': dashboard_data,
            'year': year,
            'month': month,
            'category_expenses_json': json.dumps(category_expenses, cls=DjangoJSONEncoder),
            'summary_json': json.dumps(summary_data, cls=DjangoJSONEncoder),
        }
        return render(request, 'dashboard/index.html', context)


class WebReportView(LoginRequiredMixin, View):
    def get(self, request):
        # Obtener filtros
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        wallet_id = request.GET.get('wallet')
        category_id = request.GET.get('category')
        tx_type = request.GET.get('type')
        subtype = request.GET.get('subtype')

        filters = {
            'date_from': date_from,
            'date_to': date_to,
            'wallet': wallet_id,
            'category': category_id,
            'type': tx_type,
            'subtype': subtype,
        }

        # Remover filtros vacíos para el servicio
        cleaned_filters = {k: v for k, v in filters.items() if v}

        # Obtener datos de reportes
        by_category = get_reports_data(request.user, 'by-category', cleaned_filters)
        by_wallet = get_reports_data(request.user, 'by-wallet', cleaned_filters)
        summary = get_reports_data(request.user, 'summary', cleaned_filters)

        # Cargar selectores del filtro
        wallets = Wallet.objects.filter(user=request.user)
        categories = Category.objects.filter(Q(user=request.user) | Q(is_default=True))

        context = {
            'by_category': by_category,
            'by_wallet': by_wallet,
            'summary': summary,
            'wallets': wallets,
            'categories': categories,
            'filters': filters,
            'by_category_json': json.dumps(by_category, cls=DjangoJSONEncoder),
            'by_wallet_json': json.dumps(by_wallet, cls=DjangoJSONEncoder),
            'summary_json': json.dumps(summary, cls=DjangoJSONEncoder),
        }
        return render(request, 'reports/index.html', context)
