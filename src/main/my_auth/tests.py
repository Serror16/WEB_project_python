from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.exceptions import TokenError
from unittest.mock import patch
from .models import User

class AuthTests(APITestCase):
    # нужно прописать, чтобы не было ошибки с определением методов
    client: APIClient

    def setUp(self):
        # базовые данные для тестов
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        self.user_data = {
            'email': 'test@example.com',
            'password': 'strongpassword123'
        }

        # тестовый объект юзера
        self.user = User.objects.create_user(**self.user_data)

    def test_register_successful(self):
        """Тест успешной регистрации нового пользователя"""
        new_user_data = {
            'email': 'new_user@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, new_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], new_user_data['email'])
        self.assertTrue(User.objects.filter(email='new_user@example.com').exists())

    @patch('my_auth.serializers.authenticate')
    def test_login_authentication_failure_mocked(self, mock_authenticate):
        """Тест ошибки логина с имитацией того, что authenticate вернул None"""
        # мок всегда вернет None (неверные креды)
        mock_authenticate.return_value = None

        response = self.client.post(self.login_url, self.user_data)

        # ошибка 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('non_field_errors', response.data)
        mock_authenticate.assert_called_once()

    @patch('my_auth.views.RefreshToken')
    def test_logout_invalid_token_mocked(self, mock_refresh_token):
        """Тест логаута с имитацией невалидного токена"""
        # юзер должен быть авторизован
        self.client.force_authenticate(user=self.user)

        # настройка, чтобы при попытке обновить токен вылетала конкретная ошибка
        mock_refresh_token.side_effect = TokenError("Test TokenError")

        response = self.client.post(self.logout_url, {'refresh': 'fake_invalid_token'})

        # ошибка 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Неверный refresh token')