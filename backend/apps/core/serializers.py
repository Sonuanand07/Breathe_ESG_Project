"""
DRF Serializers for Breathe ESG API.
"""

from rest_framework import serializers
from apps.core.models import (
    Client, DataSource, EmissionRecord, SAPRecord, 
    UtilityRecord, TravelRecord, AuditLog, IngestionJob
)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'legal_entity_id', 'country', 'fiscal_year_start', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class DataSourceSerializer(serializers.ModelSerializer):
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    
    class Meta:
        model = DataSource
        fields = ['id', 'client', 'source_type', 'source_type_display', 'name', 'is_active', 'last_ingestion_at', 'last_ingestion_record_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'last_ingestion_at', 'last_ingestion_record_count']


class SAPRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SAPRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class UtilityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class TravelRecordSerializer(serializers.ModelSerializer):
    travel_mode_display = serializers.CharField(source='get_travel_mode_display', read_only=True)
    
    class Meta:
        model = TravelRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'action_display', 'description', 'old_values', 'new_values', 'user_name', 'timestamp']
        read_only_fields = fields


class EmissionRecordDetailSerializer(serializers.ModelSerializer):
    """Detailed view of an emission record with related data."""
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    sap_record = SAPRecordSerializer(read_only=True, allow_null=True)
    utility_record = UtilityRecordSerializer(read_only=True, allow_null=True)
    travel_record = TravelRecordSerializer(read_only=True, allow_null=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)
    data_source_name = serializers.CharField(source='data_source.name', read_only=True, allow_null=True)
    
    class Meta:
        model = EmissionRecord
        fields = [
            'id', 'client', 'data_source', 'data_source_name',
            'scope', 'scope_display', 'category', 
            'source_data', 'source_identifier',
            'quantity', 'unit', 'unit_display',
            'co2e_kg', 'transaction_date', 'reporting_period_start', 'reporting_period_end',
            'location', 'business_unit',
            'review_status', 'review_status_display', 'flagged_reason',
            'reviewed_by_name', 'reviewed_at', 'quality_score',
            'sap_record', 'utility_record', 'travel_record',
            'audit_logs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'co2e_kg', 'reviewed_at', 'created_at', 'updated_at']


class EmissionRecordListSerializer(serializers.ModelSerializer):
    """Lightweight list view for dashboard."""
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)
    data_source_name = serializers.CharField(source='data_source.name', read_only=True, allow_null=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = EmissionRecord
        fields = [
            'id', 'scope', 'scope_display', 'category', 'quantity', 'co2e_kg',
            'transaction_date', 'location', 'review_status', 'review_status_display',
            'quality_score', 'data_source_name', 'flagged_reason', 'reviewed_by_name'
        ]
        read_only_fields = fields


class EmissionRecordUpdateSerializer(serializers.ModelSerializer):
    """For updating emission records (review workflow)."""
    
    class Meta:
        model = EmissionRecord
        fields = ['review_status', 'flagged_reason', 'location', 'business_unit']


class IngestionJobSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='data_source.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = IngestionJob
        fields = [
            'id', 'data_source', 'source_name', 'status', 'status_display',
            'original_filename', 'total_records', 'successful_records', 'failed_records',
            'error_log', 'started_at', 'completed_at', 'created_by_name'
        ]
        read_only_fields = fields
