from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .adapters import get_adapter
import uuid


class TaxReportView(APIView):
    """ Эндпоинт для подачи отчета: POST /api/v1/tax/report """

    def post(self, request, format=None):
        country = request.query_params.get('country')
        data = request.data

        if not country:
            return Response({"error": "Country required"}, status=400)

        adapter = get_adapter(country)
        result = adapter.send_report(data)

        return Response({
            "status": "accepted",
            "details": result,
            "report_id": str(uuid.uuid4())
        }, status=status.HTTP_201_CREATED)

class TaxStatusView(APIView):
    """ Проверка статуса: GET /api/v1/tax/status/{id} """

    def get(self, request, report_id, format=None):
        country = request.query_params.get('country', 'russia') # в будущем нужно будт брать страну из БД по id, а не из query параметров

        adapter = get_adapter(country)
        result = adapter.get_status(report_id)

        return Response(result, status=status.HTTP_200_OK)
    
class TaxValidateView(APIView):
    """ Эндпоинт для предварительной проверки данных: POST /api/v1/tax/validate """
    
    def post(self, request, format=None):
        country = request.query_params.get('country')
        if not country:
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Параметр 'country' обязателен"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        adapter = get_adapter(country)
        validation_result = adapter.validate(request.data)
        
        return Response(validation_result, status=status.HTTP_200_OK)
