from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .services import get_dashboard_data, get_reports_data


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            year_val = request.query_params.get('year')
            month_val = request.query_params.get('month')
            
            year = int(year_val) if year_val else None
            month = int(month_val) if month_val else None
            
            if month and (month < 1 or month > 12):
                return Response({"detail": "El mes debe estar entre 1 y 12."}, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({"detail": "Año y mes deben ser números enteros."}, status=status.HTTP_400_BAD_REQUEST)

        data = get_dashboard_data(request.user, year, month)
        return Response(data, status=status.HTTP_200_OK)


class ReportBaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    report_type = None

    def get_filters(self, request):
        return {
            'date_from': request.query_params.get('date_from'),
            'date_to': request.query_params.get('date_to'),
            'wallet': request.query_params.get('wallet'),
            'category': request.query_params.get('category'),
            'type': request.query_params.get('type'),
            'subtype': request.query_params.get('subtype'),
        }

    def get(self, request):
        filters = self.get_filters(request)
        data = get_reports_data(request.user, self.report_type, filters)
        return Response(data, status=status.HTTP_200_OK)


class CategoryReportView(ReportBaseView):
    report_type = 'by-category'


class WalletReportView(ReportBaseView):
    report_type = 'by-wallet'


class MonthlyComparisonReportView(ReportBaseView):
    report_type = 'monthly-comparison'


class YearlyComparisonReportView(ReportBaseView):
    report_type = 'yearly-comparison'


class SummaryReportView(ReportBaseView):
    report_type = 'summary'
