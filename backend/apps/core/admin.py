"""
Django admin configuration for Breathe ESG.
"""

from django.contrib import admin
from apps.core.models import (
    Client, DataSource, EmissionRecord, SAPRecord, 
    UtilityRecord, TravelRecord, AuditLog, IngestionJob
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'legal_entity_id', 'country', 'is_active', 'created_at']
    search_fields = ['name', 'legal_entity_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'source_type', 'is_active', 'last_ingestion_at']
    list_filter = ['source_type', 'is_active']
    search_fields = ['name', 'client__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_ingestion_at']


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'scope', 'category', 'review_status', 'co2e_kg', 'transaction_date']
    list_filter = ['scope', 'category', 'review_status', 'transaction_date']
    search_fields = ['source_identifier', 'category', 'location']
    readonly_fields = ['id', 'co2e_kg', 'created_at', 'updated_at']
    fields = [
        'client', 'data_source', 'scope', 'category',
        'source_identifier', 'quantity', 'unit', 'co2e_kg',
        'transaction_date', 'reporting_period_start', 'reporting_period_end',
        'location', 'business_unit',
        'review_status', 'flagged_reason', 'reviewed_by', 'reviewed_at',
        'quality_score', 'created_at', 'updated_at'
    ]


@admin.register(SAPRecord)
class SAPRecordAdmin(admin.ModelAdmin):
    list_display = ['emission_record', 'plant_code', 'material_number', 'fuel_type']
    search_fields = ['plant_code', 'material_number', 'vendor_name']
    readonly_fields = ['id', 'created_at']


@admin.register(UtilityRecord)
class UtilityRecordAdmin(admin.ModelAdmin):
    list_display = ['emission_record', 'meter_id', 'facility_name', 'utility_provider']
    search_fields = ['meter_id', 'facility_name']
    readonly_fields = ['id', 'created_at']


@admin.register(TravelRecord)
class TravelRecordAdmin(admin.ModelAdmin):
    list_display = ['emission_record', 'travel_mode', 'trip_id']
    list_filter = ['travel_mode']
    search_fields = ['trip_id', 'airline']
    readonly_fields = ['id', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['emission_record', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['emission_record__id', 'user__username']
    readonly_fields = ['id', 'timestamp']


@admin.register(IngestionJob)
class IngestionJobAdmin(admin.ModelAdmin):
    list_display = ['data_source', 'status', 'total_records', 'successful_records', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['original_filename', 'data_source__name']
    readonly_fields = ['id', 'started_at', 'completed_at']
