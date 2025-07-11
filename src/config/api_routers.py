"""
Configures the API routers for the Django application.
"""

from importlib import import_module

from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

urlpatterns = []
api_routers = DefaultRouter()

for api_app in getattr(settings, "API_APPS", []):
    api_module = import_module(f"{api_app}.apis", "apps")

    for viewset in api_module.apps:
        api_routers.register(viewset.resource_name, viewset, viewset.resource_name)


if not settings.IS_PROD:
    urlpatterns = [
        path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
        # Swagger UI for API documentation
        path(
            "docs/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        # Redoc UI for API documentation
        path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]

urlpatterns += [
    path("", include(api_routers.urls)),
]
