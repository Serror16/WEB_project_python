from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .adapters import get_adapter
from .serializers import TaxReportSerializer
import uuid


class TaxReportView(APIView):
    """ Эндпоинт для подачи отчета: POST /api/v1/tax/report """

    def post(self, request, format=None):
        country = request.query_params.get('country')
        if not country:
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Параметр 'country' обязателен",
                "details": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['country'] = country

        # вот тута чистые данные из сериализатора загоняем в адаптер
        serializer = TaxReportSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Ошибка валидации данных",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_data = serializer.validated_data
        adapter = get_adapter(country)

        try:
            result = adapter.send_report(valid_data)
            return Response({
                "status": "accepted",
                "report_id": str(uuid.uuid4()),
                "adapter_details": result
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error_code": "EXTERNAL_SERVICE_ERROR",
                "message": str(e),
                "details": {}
            }, status=status.HTTP_502_BAD_GATEWAY)


class TaxStatusView(APIView):
    """ Проверка статуса: GET /api/v1/tax/status/{report_id} """

    def get(self, request, report_id, format=None):
        country = request.query_params.get('country', 'russia')

        adapter = get_adapter(country)
        try:
            result = adapter.get_status(report_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error_code": "NOT_FOUND",
                "message": f"Отчет {report_id} не найден или сервис недоступен",
                "details": {"error": str(e)}
            }, status=status.HTTP_404_NOT_FOUND)


class TaxValidateView(APIView):
    """ Эндпоинт для предварительной проверки данных: POST /api/v1/tax/validate """

    def post(self, request, format=None):
        country = request.query_params.get('country')
        if not country:
            return Response({
                "error_code": "VALIDATION_ERROR",
                "message": "Параметр 'country' обязателен"
            }, status=status.HTTP_400_BAD_REQUEST)

        # вот тута чистые данные из сериализатора загоняем в адаптер
        serializer = TaxReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "is_valid": False,
                "error_code": "VALIDATION_ERROR",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        adapter = get_adapter(country)
        validation_result = adapter.validate(serializer.validated_data)

        return Response(validation_result, status=status.HTTP_200_OK)