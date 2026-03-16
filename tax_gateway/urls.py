from django.urls import path
from .views import TaxReportView, TaxStatusView, TaxValidateView # Добавьте импорт

urlpatterns = [
    path('report/', TaxReportView.as_view(), name='tax-report'),
    path('status/<str:report_id>', TaxStatusView.as_view(), name='tax-status'),
    path('validate/', TaxValidateView.as_view(), name='tax-validate'),
]