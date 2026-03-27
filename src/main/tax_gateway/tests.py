import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

User = get_user_model()


class TaxReportViewTests(APITestCase):
    # нужно прописать, чтобы не было ошибки с определением методов
    client: APIClient

    def setUp(self):
        # создание объекта юзера и его авторизация
        self.user = User.objects.create_user(email='tax_admin@example.com', password='strong_password')
        self.client.force_authenticate(user=self.user)

        # базовый юрл для эндпоинта
        self.url = reverse('tax-report')

        # валидный json-запрос
        self.valid_payload = {
            "idempotency_key": str(uuid.uuid4()),
            "taxpayer_id": "7707083893",
            "amount": "150000.00",
            "currency": "RUB",
            "year": 2024,
            # эти два поля уйдут в payload
            "inn": "123456789",
            "bik": "044525225"
        }

    def test_report_missing_country_param(self):
        """Проверка ошибки 400, если забыли передать параметр ?country="""
        response = self.client.post(self.url, self.valid_payload, format='json')

        # 400 с кодом VALIDATION_ERROR (ошибка валидации)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error_code'], 'VALIDATION_ERROR')

    @patch('tax_gateway.views.get_adapter')
    def test_report_success_mocked(self, mock_get_adapter):
        """Проверка успешной маршрутизации и ответа 201"""
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.send_report.return_value = {"protocol": "REST", "info": "Mocked success"}
        mock_get_adapter.return_value = mock_adapter_instance

        # запрос с параметром страны
        url_with_param = f"{self.url}?country=Russia"
        response = self.client.post(url_with_param, self.valid_payload, format='json')

        # ответ должен быть успешным и содержать сгенеренный айди
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'accepted')
        self.assertIn('report_id', response.data)

        # проверка, что адаптер вызван с верными данными
        mock_get_adapter.assert_called_once_with('Russia')
        mock_adapter_instance.send_report.assert_called_once()

        # проверка, что лишние поля запихались в payload
        called_args = mock_adapter_instance.send_report.call_args[0][0]
        self.assertIn('payload', called_args)
        self.assertEqual(called_args['payload']['inn'], "123456789")

    @patch('tax_gateway.views.get_adapter')
    def test_report_external_service_down(self, mock_get_adapter):
        """Проверка, что Gateway ловит ошибку внешнего сервиса и отдает 502 Bad Gateway"""
        mock_adapter_instance = MagicMock()
        # тут мок выбрасывает исключение
        mock_adapter_instance.send_report.side_effect = Exception("Connection timeout")
        mock_get_adapter.return_value = mock_adapter_instance

        url_with_param = f"{self.url}?country=Russia"
        response = self.client.post(url_with_param, self.valid_payload, format='json')

        # 502 и ошибка внешнего сервиса
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data['error_code'], 'EXTERNAL_SERVICE_ERROR')
        self.assertIn("Connection timeout", response.data['message'])