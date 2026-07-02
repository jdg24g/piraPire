from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import permissions
from .services import generate_transactions_csv


class ExportTransactionsCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        filters = {
            'date_from': request.query_params.get('date_from'),
            'date_to': request.query_params.get('date_to'),
            'wallet': request.query_params.get('wallet'),
            'category': request.query_params.get('category'),
            'type': request.query_params.get('type'),
            'subtype': request.query_params.get('subtype'),
        }

        csv_data = generate_transactions_csv(request.user, filters)
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions_export.csv"'
        return response
