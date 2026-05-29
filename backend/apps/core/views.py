"""
REST API views for Breathe ESG.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import logging

from apps.core.models import (
    Client, DataSource, EmissionRecord, AuditLog, IngestionJob, SAPRecord, UtilityRecord, TravelRecord
)
from apps.core.serializers import (
    ClientSerializer, DataSourceSerializer, EmissionRecordDetailSerializer,
    EmissionRecordListSerializer, EmissionRecordUpdateSerializer, IngestionJobSerializer
)
from apps.ingestion.parsers import SAPParser, UtilityParser, TravelParser

logger = logging.getLogger(__name__)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clients.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'legal_entity_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing data sources.
    """
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['source_type', 'is_active']
    search_fields = ['name']
    
    def get_queryset(self):
        client_id = self.request.query_params.get('client')
        queryset = DataSource.objects.all()
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset


class EmissionRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reviewing and managing emission records.
    
    This is the core of the analyst review dashboard.
    Provides filtering, bulk actions, and audit trail tracking.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'data_source', 'scope', 'category', 'review_status', 'quality_score']
    search_fields = ['source_identifier', 'category', 'location', 'business_unit']
    ordering_fields = ['created_at', 'quality_score', 'co2e_kg', 'transaction_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = EmissionRecord.objects.select_related(
            'client', 'data_source', 'reviewed_by',
            'sap_record', 'utility_record', 'travel_record'
        ).prefetch_related('audit_logs')
        
        # Filter by client if specified
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmissionRecordListSerializer
        elif self.action in ['update', 'partial_update']:
            return EmissionRecordUpdateSerializer
        return EmissionRecordDetailSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an emission record."""
        record = self.get_object()
        
        with transaction.atomic():
            record.review_status = 'approved'
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.save()
            
            # Create audit log
            AuditLog.objects.create(
                emission_record=record,
                action='approved',
                description=f"Approved by {request.user.get_full_name()}",
                user=request.user
            )
        
        return Response({
            'id': record.id,
            'review_status': record.review_status,
            'reviewed_at': record.reviewed_at
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an emission record."""
        record = self.get_object()
        reason = request.data.get('reason', '')
        
        with transaction.atomic():
            record.review_status = 'rejected'
            record.flagged_reason = reason
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.save()
            
            # Create audit log
            AuditLog.objects.create(
                emission_record=record,
                action='rejected',
                description=f"Rejected by {request.user.get_full_name()}: {reason}",
                user=request.user
            )
        
        return Response({
            'id': record.id,
            'review_status': record.review_status,
            'flagged_reason': reason
        })
    
    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        """Flag a record for further analysis."""
        record = self.get_object()
        reason = request.data.get('reason', '')
        
        with transaction.atomic():
            record.review_status = 'flagged'
            record.flagged_reason = reason
            record.save()
            
            # Create audit log
            AuditLog.objects.create(
                emission_record=record,
                action='flagged',
                description=f"Flagged by {request.user.get_full_name()}: {reason}",
                user=request.user
            )
        
        return Response({
            'id': record.id,
            'review_status': record.review_status,
            'flagged_reason': reason
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get summary statistics for the dashboard."""
        client = request.query_params.get('client')
        
        queryset = EmissionRecord.objects.all()
        if client:
            queryset = queryset.filter(client_id=client)
        
        return Response({
            'total_records': queryset.count(),
            'pending': queryset.filter(review_status='pending').count(),
            'flagged': queryset.filter(review_status='flagged').count(),
            'approved': queryset.filter(review_status='approved').count(),
            'rejected': queryset.filter(review_status='rejected').count(),
            'total_co2e_kg': sum(r.co2e_kg for r in queryset),
            'by_scope': {
                'scope_1': queryset.filter(scope='scope_1').count(),
                'scope_2': queryset.filter(scope='scope_2').count(),
                'scope_3': queryset.filter(scope='scope_3').count(),
            }
        })


class DataIngestionViewSet(viewsets.ViewSet):
    """
    Handle file uploads and data ingestion.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    @action(detail=False, methods=['post'], url_path='sap')
    def ingest_sap(self, request):
        """Upload and ingest SAP data."""
        return self._ingest_file(request, 'sap', SAPParser.parse_csv)
    
    @action(detail=False, methods=['post'], url_path='utility')
    def ingest_utility(self, request):
        """Upload and ingest utility data."""
        return self._ingest_file(request, 'utility', UtilityParser.parse_csv)
    
    @action(detail=False, methods=['post'], url_path='travel')
    def ingest_travel(self, request):
        """Upload and ingest travel data."""
        return self._ingest_file(request, 'travel', TravelParser.parse_csv)
    
    def _ingest_file(self, request, source_type: str, parser_func):
        """Generic file ingestion handler."""
        try:
            # Validate request
            client_id = request.data.get('client_id')
            data_source_id = request.data.get('data_source_id')
            file_obj = request.FILES.get('file')
            
            if not all([client_id, data_source_id, file_obj]):
                return Response(
                    {'error': 'Missing required fields: client_id, data_source_id, file'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get client and data source
            client = get_object_or_404(Client, id=client_id)
            data_source = get_object_or_404(DataSource, id=data_source_id, client=client)
            
            # Read file
            file_content = file_obj.read().decode('utf-8')
            
            # Create ingestion job
            job = IngestionJob.objects.create(
                data_source=data_source,
                original_filename=file_obj.name,
                created_by=request.user,
                status='processing'
            )
            
            # Parse data
            with transaction.atomic():
                parsed_records, errors = parser_func(file_content, client, data_source)
                
                # Create EmissionRecords
                created_count = 0
                for record_data in parsed_records:
                    try:
                        # Extract source-specific data
                        sap_data = record_data.pop('sap_data', {})
                        utility_data = record_data.pop('utility_data', {})
                        travel_data = record_data.pop('travel_data', {})
                        
                        # Create main record
                        emission_record = EmissionRecord.objects.create(**record_data)
                        
                        # Create source-specific records
                        if sap_data:
                            SAPRecord.objects.create(
                                emission_record=emission_record,
                                **sap_data
                            )
                        elif utility_data:
                            UtilityRecord.objects.create(
                                emission_record=emission_record,
                                **utility_data
                            )
                        elif travel_data:
                            TravelRecord.objects.create(
                                emission_record=emission_record,
                                **travel_data
                            )
                        
                        # Create audit log
                        AuditLog.objects.create(
                            emission_record=emission_record,
                            action='created',
                            description=f"Created from {source_type} ingestion",
                            user=request.user
                        )
                        
                        created_count += 1
                    
                    except Exception as e:
                        errors.append(f"Failed to create record: {str(e)}")
                        logger.error(f"Record creation failed: {e}")
                
                # Update job
                job.total_records = len(parsed_records)
                job.successful_records = created_count
                job.failed_records = len(errors)
                job.error_log = errors
                job.status = 'completed' if not errors else 'partial'
                job.completed_at = timezone.now()
                job.save()
                
                # Update data source last ingestion
                data_source.last_ingestion_at = timezone.now()
                data_source.last_ingestion_record_count = created_count
                data_source.save()
            
            return Response({
                'job_id': job.id,
                'status': job.status,
                'total_records': job.total_records,
                'successful_records': job.successful_records,
                'failed_records': job.failed_records,
                'errors': errors[:10],  # Return first 10 errors
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return Response(
                {'error': f'Ingestion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IngestionJobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View ingestion job history and results.
    """
    serializer_class = IngestionJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['data_source', 'status']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
    
    def get_queryset(self):
        return IngestionJob.objects.select_related('data_source', 'created_by')
