from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataFactoryViewSet

router = DefaultRouter()
router.register(r'', DataFactoryViewSet, basename='data-factory')

urlpatterns = [
    path('', include(router.urls)),
]
