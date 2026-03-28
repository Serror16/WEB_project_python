from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/v1/tax/', include('tax_gateway.urls')),
    path("api/auth/", include("my_auth.urls")),

    #Api documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]