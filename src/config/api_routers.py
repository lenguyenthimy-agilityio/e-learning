"""
Configures the API routers for the Django application.
"""

from importlib import import_module

from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

urlpatterns = []
api_routers = DefaultRouter()

for api_app in getattr(settings, "API_APPS", []):
    api_module = import_module(f"{api_app}.apis.views", "apps")

    for viewset in api_module.apis:
        api_routers.register(viewset.resource_name, viewset, viewset.resource_name)


urlpatterns += [
    path("", include(api_routers.urls)),
]
