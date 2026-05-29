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

# Ingestion endpoints
ingestion_patterns = [
    path('ingest-sap/', views.DataIngestionViewSet.as_view({'post': 'ingest_sap'}), name='ingest-sap'),
    path('ingest-utility/', views.DataIngestionViewSet.as_view({'post': 'ingest_utility'}), name='ingest-utility'),
    path('ingest-travel/', views.DataIngestionViewSet.as_view({'post': 'ingest_travel'}), name='ingest-travel'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('ingestion/', include(ingestion_patterns)),
]
