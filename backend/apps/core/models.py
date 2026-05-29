"""
Core data models for Breathe ESG.

This model implements:
1. Multi-tenancy (Client organizations)
2. Scope 1/2/3 categorization per GHG Protocol
3. Source-of-truth tracking (data provenance)
4. Unit normalization and conversion
5. Complete audit trail for compliance
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid


class Client(models.Model):
    """
    Represents an enterprise client company.
    
    Multi-tenancy at the client level ensures data isolation
    and supports multiple organizations with different data sources.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    legal_entity_id = models.CharField(max_length=50, unique=True, help_text="Company registration number or ID")
    country = models.CharField(max_length=2, default='US', help_text="ISO 3166-1 alpha-2 country code")
    fiscal_year_start = models.DateField(help_text="Start date of fiscal year for reporting periods")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DataSourceType(models.TextChoices):
    """Types of data sources we ingest."""
    SAP = 'sap', 'SAP (Fuel & Procurement)'
    UTILITY = 'utility', 'Utility (Electricity)'
    TRAVEL = 'travel', 'Corporate Travel'


class DataSource(models.Model):
    """
    Tracks data sources for a client.
    
    Each client can have multiple data sources of each type,
    allowing us to distinguish between different SAP instances,
    multiple utility providers, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='data_sources')
    
    source_type = models.CharField(max_length=20, choices=DataSourceType.choices)
    name = models.CharField(max_length=255, help_text="Human-readable name (e.g., 'SAP ERP Instance 1')")
    
    # Connection details (encrypted in production)
    configuration = models.JSONField(default=dict, help_text="JSON config for this source")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Tracking of last successful ingestion
    last_ingestion_at = models.DateTimeField(null=True, blank=True)
    last_ingestion_record_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = [['client', 'source_type', 'name']]
        ordering = ['source_type', 'name']
    
    def __str__(self):
        return f"{self.get_source_type_display()} - {self.name}"


class ScopeCategory(models.TextChoices):
    """
    GHG Protocol scopes.
    
    Scope 1: Direct emissions (company owns/controls sources)
    Scope 2: Indirect energy emissions (purchased electricity, steam, etc.)
    Scope 3: Other indirect emissions (business travel, employee commute, etc.)
    """
    SCOPE_1 = 'scope_1', 'Scope 1 - Direct Emissions'
    SCOPE_2 = 'scope_2', 'Scope 2 - Purchased Energy'
    SCOPE_3 = 'scope_3', 'Scope 3 - Other Indirect Emissions'


class Unit(models.TextChoices):
    """Standard units for emissions data."""
    # Energy/Volume
    LITER = 'L', 'Liters'
    GALLON = 'gal', 'US Gallons'
    CUBIC_METER = 'm3', 'Cubic Meters'
    
    # Mass
    KG = 'kg', 'Kilograms'
    METRIC_TON = 'mt', 'Metric Tons'
    POUND = 'lb', 'Pounds'
    
    # Energy
    KWH = 'kWh', 'Kilowatt-hours'
    MWH = 'MWh', 'Megawatt-hours'
    MMBTU = 'MMBtu', 'Million BTU'
    
    # Distance
    KM = 'km', 'Kilometers'
    MILE = 'mi', 'Miles'
    
    # Others
    UNIT = 'unit', 'Units (generic)'


class ReviewStatus(models.TextChoices):
    """Status of data record in the review pipeline."""
    PENDING = 'pending', 'Pending Review'
    FLAGGED = 'flagged', 'Flagged for Analysis'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class EmissionRecord(models.Model):
    """
    Base model for all emission-related data records.
    
    This is the central record that all data sources feed into.
    It tracks:
    - The raw data as received
    - Normalized/calculated values
    - Which source produced it
    - Review status for analyst approval
    - Full audit trail
    
    We use Scope 1/2/3 categorization per GHG Protocol.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emission_records')
    data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Classification
    scope = models.CharField(max_length=20, choices=ScopeCategory.choices)
    category = models.CharField(
        max_length=50,
        help_text="Subcategory (e.g., 'fleet_fuel', 'purchased_electricity', 'business_flights')"
    )
    
    # Source data (raw, as received)
    source_data = models.JSONField(default=dict, help_text="Raw data as received from source")
    source_identifier = models.CharField(
        max_length=255,
        help_text="Source's unique ID for this record (e.g., PO number, meter ID, trip ID)"
    )
    
    # Normalized values
    quantity = models.DecimalField(
        max_digits=15, decimal_places=6, validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=20, choices=Unit.choices)
    
    # Calculated emissions
    co2e_kg = models.DecimalField(
        max_digits=15, decimal_places=6, validators=[MinValueValidator(0)],
        help_text="CO2 equivalent in kilograms (calculated from quantity + emission factor)"
    )
    
    # Date/period information
    transaction_date = models.DateField(help_text="Date the emission occurred")
    reporting_period_start = models.DateField(help_text="Start of reporting period")
    reporting_period_end = models.DateField(help_text="End of reporting period")
    
    # Metadata
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Where the emission occurred (plant code, facility, etc.)"
    )
    business_unit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organizational unit responsible for this emission"
    )
    
    # Review workflow
    review_status = models.CharField(
        max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    flagged_reason = models.TextField(blank=True, help_text="Why this record was flagged")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_records'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Confidence score (0-100) for auto-detection of issues
    quality_score = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    
    class Meta:
        indexes = [
            models.Index(fields=['client', 'review_status']),
            models.Index(fields=['client', 'scope']),
            models.Index(fields=['data_source', 'review_status']),
            models.Index(fields=['transaction_date']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_scope_display()} - {self.category} - {self.transaction_date}"


class SAPRecord(models.Model):
    """
    SAP-specific details for fuel and procurement data.
    
    SAP modules: MM (Materials Management) for procurement,
    FI-CA for fuels. We store SAP-specific fields that don't fit
    the generic EmissionRecord model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission_record = models.OneToOneField(EmissionRecord, on_delete=models.CASCADE, related_name='sap_record')
    
    # SAP document identifiers
    purchase_order_number = models.CharField(max_length=100, blank=True)
    document_number = models.CharField(max_length=100, blank=True)
    document_line = models.CharField(max_length=10, blank=True)
    plant_code = models.CharField(max_length=10, help_text="SAP plant code (WERKS)")
    
    # Material/fuel information
    material_number = models.CharField(max_length=50, help_text="SAP material number (MATNR)")
    material_description = models.CharField(max_length=255, blank=True)
    fuel_type = models.CharField(
        max_length=50,
        help_text="Type of fuel (Gasoline, Diesel, Natural Gas, etc.)"
    )
    
    # Vendor/supplier
    vendor_code = models.CharField(max_length=50, blank=True)
    vendor_name = models.CharField(max_length=255, blank=True)
    
    # Cost center
    cost_center = models.CharField(max_length=50, blank=True)
    order_number = models.CharField(max_length=50, blank=True)
    
    # Invoice details
    invoice_number = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    
    # Original SAP units before conversion
    original_quantity = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True
    )
    original_unit = models.CharField(max_length=20, blank=True)
    
    # Quality tracking
    parsing_notes = models.TextField(blank=True, help_text="Notes from data parsing/normalization")
    unit_conversion_applied = models.CharField(
        max_length=255, blank=True,
        help_text="Description of unit conversion applied (e.g., 'gal to L: x 3.78541')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SAP {self.plant_code} - {self.material_description}"


class UtilityRecord(models.Model):
    """
    Utility/electricity billing data.
    
    Utilities provide meter readings with:
    - Multiple meters per facility
    - Billing periods (not always calendar months)
    - Complex tariff structures
    - Seasonal variations
    
    We normalize to monthly or actual billing period.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission_record = models.OneToOneField(EmissionRecord, on_delete=models.CASCADE, related_name='utility_record')
    
    # Meter identification
    meter_id = models.CharField(max_length=100, help_text="Utility's meter identification number")
    meter_serial = models.CharField(max_length=100, blank=True)
    
    # Facility information
    facility_name = models.CharField(max_length=255)
    facility_code = models.CharField(max_length=50, blank=True)
    utility_account_number = models.CharField(max_length=100, blank=True)
    
    # Utility company
    utility_provider = models.CharField(max_length=255, help_text="Name of the utility company")
    utility_type = models.CharField(
        max_length=50,
        help_text="Type: Electricity, Natural Gas, Water, etc.",
        default='Electricity'
    )
    
    # Meter readings
    opening_read = models.DecimalField(max_digits=15, decimal_places=6)
    closing_read = models.DecimalField(max_digits=15, decimal_places=6)
    read_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Actual, Estimated, or Derived"
    )
    
    # Billing period
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    billing_cycle_days = models.IntegerField(help_text="Number of days in billing period")
    
    # Tariff information
    tariff_name = models.CharField(max_length=255, blank=True)
    tariff_rate_per_unit = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True,
        help_text="Rate per unit (for simple tariffs)"
    )
    
    # Loss factor (for transmission/distribution)
    transmission_loss_factor = models.DecimalField(
        max_digits=5, decimal_places=4, default=1.0,
        help_text="Factor to account for transmission losses (typically 1.0-1.1)"
    )
    
    # Invoice details
    invoice_number = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    
    # Parsing notes
    parsing_notes = models.TextField(blank=True)
    pdf_extracted = models.BooleanField(
        default=False, help_text="Was this data extracted from a PDF bill?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-billing_period_end']
    
    def __str__(self):
        return f"{self.meter_id} - {self.facility_name} ({self.billing_period_start})"


class TravelRecord(models.Model):
    """
    Corporate travel data from Concur/Navan.
    
    Includes:
    - Flights (with distance calculation from airport codes if needed)
    - Hotels (occupancy-based emissions)
    - Ground transport (rental cars, taxis, trains)
    
    Different emission factors apply per travel mode.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission_record = models.OneToOneField(EmissionRecord, on_delete=models.CASCADE, related_name='travel_record')
    
    # Trip identification
    trip_id = models.CharField(max_length=100, help_text="Platform's trip/expense ID")
    employee_id = models.CharField(max_length=100, blank=True)
    
    # Travel mode
    TRAVEL_MODES = [
        ('flight', 'Flight'),
        ('hotel', 'Hotel'),
        ('rental_car', 'Rental Car'),
        ('taxi', 'Taxi/Rideshare'),
        ('train', 'Train'),
        ('bus', 'Bus'),
    ]
    travel_mode = models.CharField(max_length=50, choices=TRAVEL_MODES)
    
    # Flight details (if applicable)
    departure_airport = models.CharField(max_length=10, blank=True, help_text="IATA code")
    arrival_airport = models.CharField(max_length=10, blank=True, help_text="IATA code")
    distance_km = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Distance in km (calculated from airports if not provided)"
    )
    airline = models.CharField(max_length=255, blank=True)
    flight_number = models.CharField(max_length=20, blank=True)
    
    # Seat class (affects emission factors)
    SEAT_CLASSES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First'),
    ]
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASSES, default='economy')
    
    # Hotel details (if applicable)
    hotel_name = models.CharField(max_length=255, blank=True)
    hotel_location = models.CharField(max_length=255, blank=True)
    number_of_nights = models.IntegerField(null=True, blank=True)
    
    # Ground transport details
    vehicle_type = models.CharField(max_length=100, blank=True)
    distance_miles = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    # Cost (for cross-validation)
    cost_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_currency = models.CharField(max_length=3, default='USD')
    
    # Emission factor used
    emission_factor_source = models.CharField(
        max_length=255,
        blank=True,
        help_text="Where we got the emission factor (e.g., 'ICAO 2022', 'Defra 2023')"
    )
    
    # Parsing notes
    parsing_notes = models.TextField(blank=True)
    distance_derived = models.BooleanField(
        default=False, help_text="Was distance calculated from airport codes?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.travel_mode == 'flight':
            return f"{self.departure_airport} → {self.arrival_airport} ({self.travel_mode})"
        elif self.travel_mode == 'hotel':
            return f"{self.hotel_name} - {self.number_of_nights} nights"
        else:
            return f"{self.travel_mode} - {self.cost_amount} {self.cost_currency}"


class AuditLog(models.Model):
    """
    Complete audit trail for compliance.
    
    Tracks all changes to EmissionRecords:
    - Initial creation
    - Normalization/parsing changes
    - Review approvals/rejections
    - Data corrections
    
    Required for audit compliance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission_record = models.ForeignKey(
        EmissionRecord, on_delete=models.CASCADE, related_name='audit_logs'
    )
    
    # What changed
    ACTION_CHOICES = [
        ('created', 'Record Created'),
        ('parsed', 'Data Parsed'),
        ('normalized', 'Data Normalized'),
        ('flagged', 'Flagged'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('updated', 'Updated'),
        ('corrected', 'Corrected'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Change details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # Who and when
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['emission_record', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.emission_record.id} - {self.get_action_display()}"


class IngestionJob(models.Model):
    """
    Tracks data ingestion jobs.
    
    When we ingest data from a source (file upload, API pull, etc.),
    we create an IngestionJob to track:
    - What was ingested
    - How many records
    - Success/failure rates
    - Detailed error log
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='ingestion_jobs')
    
    # Status
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partial Failure'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # File information
    original_filename = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash of uploaded file")
    
    # Statistics
    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)
    
    # Error log
    error_log = models.JSONField(default=list, help_text="List of error details")
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Created by
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.data_source.name} - {self.original_filename}"
