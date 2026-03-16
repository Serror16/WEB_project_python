from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#ДАНЯ ЭТО ЗАГЛУШКА СЕРИАЛИЗАТОРА
class MockSerializer:
    def __init__(self, data):
        self.data = data
        self.is_valid = True

class TaxReportView(APIView):
    """ Эндпоинт для подачи отчета: POST /api/v1/tax/report """

    def post(self, request):
        country = request.query_params.get('country')

        if not country:
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Параметр 'country' обязателен",
                "details": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #Вызов зашлушки вместо реального сериализатора
        serializer = MockSerializer(data=request.data)
        
        if serializer.is_valid:
            return Response({
                "status": "accepted",
                "report_id": "mock_id_12345",
                "timestamp": "2026-03-16T17:20:00Z"
            }, status=status.HTTP_201_CREATED)

class TaxStatusView(APIView):
    """ Проверка статуса: GET /api/v1/tax/status/{id} """
    def get(self, request, report_id):
        return Response({
            "report_id": report_id,
            "status": "in_progress"
        }, status=status.HTTP_200_OK)
    
class TaxValidateView(APIView):
    """ Эндпоинт для предварительной проверки данных: POST /api/v1/tax/validate """

    def post(self, request):
        country = request.query_params.get('country')

        if not country:
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Параметр 'country' обязателен",
                "details": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        #Вызов зашлушки вместо реального сериализатора
        serializer = MockSerializer(data=request.data)

        if serializer.is_valid:
            return Response({
                "is_valid": True,
                "message": f"Данные корректны для юрисдикции: {country}",
                "errors": []
            }, status=status.HTTP_200_OK)
        
        return Response({
            "is_valid": False,
            "errors": []
        }, status=status.HTTP_200_OK)
