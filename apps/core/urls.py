from django.urls import path, include
from apps.core.views import TestAPIView


urlpatterns = [
    path('', include('apps.core.api.routers')),
    path('test/', TestAPIView.as_view(), name="test"),
]
