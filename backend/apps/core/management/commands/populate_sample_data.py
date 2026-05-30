"""
Management command to populate initial sample data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging

from apps.core.models import (
    Client, DataSource, DataSourceType, EmissionRecord, ScopeCategory, Unit, ReviewStatus
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate initial sample data for Breathe ESG'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before populating')

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(
            username='analyst@breatheesg.com',
            defaults={
                'email': 'analyst@breatheesg.com',
                'first_name': 'Demo',
                'last_name': 'Analyst',
                'is_staff': False
            }
        )

        if created:
            user.set_password('demo1234')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created demo user'))
        else:
            self.stdout.write(self.style.WARNING('• Demo user already exists'))

        # Create sample clients
        clients_data = [
            {
                'name': 'Tech Corp Inc',
                'legal_entity_id': 'TC-2024-001',
                'country': 'US',
            },
            {
                'name': 'Green Manufacturing Ltd',
                'legal_entity_id': 'GM-2024-001',
                'country': 'UK',
            },
            {
                'name': 'Global Services GmbH',
                'legal_entity_id': 'GS-2024-001',
                'country': 'DE',
            },
        ]

        created_clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                name=client_data['name'],
                defaults={
                    'legal_entity_id': client_data['legal_entity_id'],
                    'country': client_data['country'],
                    'fiscal_year_start': timezone.now().date().replace(month=1, day=1),
                }
            )
            created_clients.append(client)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created client: {client.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'• Client already exists: {client.name}'))

        # Create sample data sources for each client
        for client in created_clients:
            sources = [
                {
                    'source_type': DataSourceType.SAP,
                    'name': f'{client.name} - SAP Instance',
                    'configuration': {'system': 'ERP', 'version': '4.7'},
                },
                {
                    'source_type': DataSourceType.UTILITY,
                    'name': f'{client.name} - Main Facility Electricity',
                    'configuration': {'provider': 'Local Utility', 'meter_id': 'MET-001'},
                },
                {
                    'source_type': DataSourceType.TRAVEL,
                    'name': f'{client.name} - Corporate Travel',
                    'configuration': {'provider': 'Concur', 'cost_center': 'TRAVEL-2024'},
                },
            ]

            for source_data in sources:
                source, created = DataSource.objects.get_or_create(
                    client=client,
                    source_type=source_data['source_type'],
                    name=source_data['name'],
                    defaults={'configuration': source_data['configuration']}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created data source: {source.name}'))

        # Create sample emission records
        for client in created_clients:
            data_sources = client.data_sources.all()
            
            for i in range(5):
                date_offset = i * 7
                transaction_date = timezone.now().date() - timedelta(days=date_offset)
                
                record = EmissionRecord.objects.create(
                    client=client,
                    data_source=data_sources.first() if data_sources.exists() else None,
                    scope=ScopeCategory.SCOPE_1,
                    category='fuel_consumption',
                    source_data={
                        'original_unit': 'L',
                        'source_system': 'SAP',
                        'plant_code': 'P001',
                    },
                    source_identifier=f'PO-{uuid.uuid4().hex[:8].upper()}',
                    quantity=Decimal('100.00'),
                    unit=Unit.LITER,
                    co2e_kg=Decimal(f'{250 + (i * 10)}.00'),
                    transaction_date=transaction_date,
                    reporting_period_start=transaction_date.replace(day=1),
                    reporting_period_end=(transaction_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                    location='Main Facility',
                    business_unit='Operations',
                    review_status=ReviewStatus.PENDING if i < 3 else ReviewStatus.APPROVED,
                    reviewed_by=user if i >= 3 else None,
                    reviewed_at=timezone.now() if i >= 3 else None,
                )
                self.stdout.write(f'  ✓ Created emission record {i+1}/5 for {client.name}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data population complete!'))
        self.stdout.write(self.style.WARNING('\nDemo Credentials:'))
        self.stdout.write('  Email: analyst@breatheesg.com')
        self.stdout.write('  Password: demo1234')
