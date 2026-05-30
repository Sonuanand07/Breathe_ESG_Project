"""
URL patterns for core app (clients, data sources, records, ingestion).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core import views

router = DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'data-sources', views.DataSourceViewSet, basename='datasource')
router.register(r'records', views.EmissionRecordViewSet, basename='record')
router.register(r'ingestion-jobs', views.IngestionJobViewSet, basename='ingestion-job')
router.register(r'ingestion', views.DataIngestionViewSet, basename='ingestion')

urlpatterns = [
    path('', include(router.urls)),
]
