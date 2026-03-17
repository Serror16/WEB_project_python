from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import TaxReportView, TaxStatusView, TaxValidateView

urlpatterns = [
    path('report/', TaxReportView.as_view(), name='tax-report'),
    re_path(r'^status/(?P<report_id>[^.]+)/?$', TaxStatusView.as_view(), name='tax-status'),
    path('validate/', TaxValidateView.as_view(), name='tax-validate'),
]

urlpatterns = format_suffix_patterns(urlpatterns)