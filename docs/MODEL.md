# Data Model Documentation

## Overview

The Breathe ESG data model is designed to ingest emissions data from three distinct sources (SAP, Utility, Corporate Travel), normalize them into a standardized format, and provide a complete audit trail for analyst review and regulatory compliance.

**Design Philosophy**: The model prioritizes data provenance, scope categorization per GHG Protocol, and audit compliance over ease of querying. Every record maintains links to its source, original data, normalization decisions, and review history.

## Core Tables

### Client (Top-Level Multi-Tenancy)

```python
Client:
  - id: UUID (primary key)
  - name: Unique organization name
  - legal_entity_id: Company registration number (for audit trail)
  - country: ISO 3166-1 code (enables region-specific emission factors)
  - fiscal_year_start: When the organization's reporting year begins
  - is_active: Soft delete capability
  - created_at, updated_at: Timestamps
```

**Justification for Multi-Tenancy at Client Level**:
- Breathe ESG is an enterprise platform serving multiple clients
- Each client has its own regulatory requirements, audit protocols, and data sensitivity
- Scope 1/2/3 categorization is client-specific (what's Scope 3 for one company might be Scope 1 for another)
- Row-level security: analysts at one client should never see another client's data
- Fiscal year varies by organization (some use calendar year, others April-March)

---

### DataSource

```python
DataSource:
  - id: UUID
  - client: FK to Client
  - source_type: Choice(SAP, UTILITY, TRAVEL)
  - name: Human identifier ("SAP ERP Prod", "Tesla Grid, Denver", "Concur API")
  - configuration: JSON (connection params, encrypted in production)
  - is_active: Enable/disable without deleting
  - last_ingestion_at: Track freshness
  - last_ingestion_record_count: Monitor volume trends
```

**Why Separate from EmissionRecord**:
- One client can have multiple SAP instances, multiple utility providers, multiple travel platforms
- Different data sources may have different ingestion schedules
- Audit trail needs to identify *which* source produced a record
- Allows disabling a source without deleting historical records
- Enables A/B testing or gradual rollout of new sources

---

### EmissionRecord (Central Fact Table)

```python
EmissionRecord:
  - id: UUID
  - client: FK to Client
  - data_source: FK to DataSource (nullable for manual entries)
  
  # Scope & Classification (GHG Protocol)
  - scope: Choice(SCOPE_1, SCOPE_2, SCOPE_3)
  - category: String ("fleet_fuel", "purchased_electricity", "business_flights", etc.)
  
  # Source Tracking (Data Provenance)
  - source_identifier: String (PO#, meter ID, trip ID - *unique per source*)
  - source_data: JSON (raw data as received - immutable audit trail)
  
  # Normalized Values
  - quantity: Decimal
  - unit: Choice (L, gal, kWh, MWh, km, mi, etc.)
  
  # Calculated
  - co2e_kg: Decimal (quantity × emission_factor)
  
  # Temporal
  - transaction_date: Date (when the emission occurred)
  - reporting_period_start, reporting_period_end: Date (for utilities with non-calendar billing)
  
  # Contextual
  - location: String (plant code, facility name, etc.)
  - business_unit: String (cost center, division, etc.)
  
  # Review Workflow
  - review_status: Choice(PENDING, FLAGGED, APPROVED, REJECTED)
  - flagged_reason: Text (why analyst flagged it)
  - reviewed_by: FK to User
  - reviewed_at: DateTime
  
  # Quality
  - quality_score: Int 0-100 (auto-detected issues reduce this)
  
  # Timestamps
  - created_at, updated_at
```

**Design Justification**:

1. **Scope Field is Critical**
   - GHG Protocol distinguishes three scopes with different materiality and audit requirements
   - Scope 3 ("other indirect") includes business travel - fundamentally different from Scope 1 fuel
   - Client may need to filter reports by scope for regulatory filing
   - Emission factors vary per scope

2. **Source Data Stored as JSON (Immutable)**
   - Original SAP/utility/travel data is *always* preserved
   - Auditors can verify that we didn't accidentally exclude or alter source data
   - If we discover a parsing bug later, we can re-parse without re-requesting from sources
   - Supports "explain this number" queries: analyst can see the raw line item

3. **Quantity + Unit (Not Pre-Converted CO2e)**
   - Different stakeholders care about different units
   - Facility team cares about kWh (cost impact)
   - ESG analyst cares about CO2e (regulatory impact)
   - Changing emission factors later (e.g., grid gets cleaner) requires recalculation from quantity
   - Stores original unit before normalization (helps debug parsing issues)

4. **Two Date Fields**
   - `transaction_date`: when the emission actually occurred
   - `reporting_period_start/end`: for utilities with 31-day or 35-day billing cycles
   - Utilities don't align with calendar months - essential for accurate period reconciliation
   - Travel might span multiple days but report on one invoice date

5. **Review Workflow Fields**
   - `review_status`: only approved records go to auditors
   - Analyst must explicitly approve, not auto-approve (compliance requirement)
   - `flagged_reason` forces analyst to document why they have concerns
   - Audit trail shows who approved and when

6. **Indexes on Common Queries**
   ```
   - (client, review_status): dashboard queries
   - (client, scope): scope-specific reports
   - (data_source, review_status): ingestion monitoring
   - (transaction_date): temporal queries
   ```

---

### SAPRecord, UtilityRecord, TravelRecord (Source-Specific Extensions)

Instead of a JSON blob, we normalize source-specific fields into separate tables:

```python
SAPRecord:
  - id: UUID
  - emission_record: OneToOne FK
  - purchase_order_number, plant_code, material_number
  - fuel_type: Specific SAP classification
  - vendor_code, vendor_name
  - cost_center, order_number
  - original_quantity, original_unit (before conversion)
  - unit_conversion_applied: String ("gal to L: × 3.78541")
  - parsing_notes: Debugging info
```

**Why Not Just Store in JSON?**
- SAP fields are structured and repeatable (indexed queries possible)
- Enables reports like "which vendors, total fuel by plant"
- JSON blobs are query-hostile
- But keeps SAP-specific fields out of the main table (cleaner schema)

---

### AuditLog (Complete Change History)

```python
AuditLog:
  - id: UUID
  - emission_record: FK
  - action: Choice(CREATED, PARSED, NORMALIZED, FLAGGED, APPROVED, REJECTED, UPDATED)
  - description: Text
  - old_values, new_values: JSON (for what changed)
  - user: FK to User
  - timestamp: DateTime (auto-now-add)
```

**Why This Matters**:
- Regulatory audits require "explain every number we report"
- AuditLog answers: "who changed this record, what did it say before, why"
- Links approval decisions to analyst usernames
- Immutable (timestamp is auto-now-add, can't be edited)

---

### IngestionJob (Ingestion Tracking)

```python
IngestionJob:
  - id: UUID
  - data_source: FK
  - status: Choice(STARTED, PROCESSING, COMPLETED, FAILED, PARTIAL)
  - original_filename: String
  - file_hash: SHA256 (detect duplicate uploads)
  - total_records, successful_records, failed_records: Int
  - error_log: JSON (list of parsing errors)
  - started_at, completed_at: DateTime
  - created_by: FK to User
```

**Why Track Jobs Separately**:
- One CSV upload might contain 500 records; one fails parsing
- Analyst needs to know: "I uploaded this file, 498 records succeeded, 2 failed with X error"
- File hash prevents accidental re-uploads
- Supports async processing (upload completes immediately, job runs in background)

---

## Unit Normalization Strategy

Different sources use different units. We standardize to one of:
- **Energy**: kWh (kilowatt-hours)
- **Volume**: L (liters) 
- **Distance**: km (kilometers)
- **Mass**: kg (kilograms)

Conversion factors are documented in `UnitConverter` class:
```python
gal → L: × 3.78541
mi → km: × 1.60934
MMBtu → kWh: × 293.071
```

**Storage**: We store BOTH:
1. Original quantity + unit (as received from source)
2. Normalized quantity + unit (for calculations)
3. Conversion description ("gal to L: × 3.78541")

This enables debugging. If SAP says "10 gallons" and we convert to 37.85 liters, the audit trail captures that.

---

## Emission Factors

CO2e is calculated as: **Quantity × Emission Factor**

Factors stored in `EmissionFactors` class (simplified for this project):

```python
FUEL = {
    'Diesel': 2.68 kg CO2e/liter,
    'Gasoline': 2.31 kg CO2e/liter,
    'Natural Gas': 2.04 kg CO2e/m³,
}

ELECTRICITY = {
    'US': 0.38 kg CO2e/kWh (average grid),
    'UK': 0.18 kg CO2e/kWh (cleaner grid),
}

FLIGHT = {
    'economy': 0.09 kg CO2e/km (per passenger),
    'business': 0.27 kg CO2e/km (3x space),
}
```

**Sources**:
- Defra/BEIS UK GHG Conversion Factors 2023
- EPA eGRID (for US electricity by region)
- ICAO Carbon Emissions Calculator (for flights with RFI multiplier)

In production, these would be:
- Versioned (track which factor set was used for which year)
- Region-specific (electricity grid carbon intensity varies widely)
- User-overridable (if client has specific contracts with utilities, use their factors)
- Auditable (log whenever a factor changes)

---

## Multi-Tenancy Security

**Access Control at Query Level**:
```python
# Only serve records for authenticated user's client
EmissionRecord.objects.filter(client=user.client)
```

**No Cross-Client Leakage**:
- Analyst at Company A cannot see Company B's data
- Supported by unique constraint on (client, legal_entity_id)
- API endpoints enforce client_id in filters

---

## Scope 1 vs 2 vs 3

| Scope | Definition | Sources in This Project |
|-------|-----------|------------------------|
| **1** | Direct emissions from sources owned/controlled by organization | SAP fuel (fleet, heating oil) |
| **2** | Indirect emissions from purchased electricity, steam, cooling | Utility electricity |
| **3** | All other indirect emissions | Business travel, hotels, ground transport |

**Why This Matters**:
- Scope 1 is "hardest" to decarbonize (requires fleet replacement)
- Scope 2 depends on grid composition (getting cleaner)
- Scope 3 includes employee commute, outsourced services, supply chain (often largest category)
- Regulatory requirements differ per scope

---

## Why Not Flat Files or NoSQL?

This project uses **PostgreSQL relational model** because:

1. **Consistency**: Ensure referential integrity (no orphaned records)
2. **Queryability**: Analyst needs to filter by scope, status, date range
3. **Indexing**: Queries like "show me all flagged Scope 2 records" are fast
4. **Joins**: EmissionRecord ← SAPRecord ← Audit trail forms a narrative
5. **Transactions**: Ingestion must be atomic (either all 500 records succeed or all fail)

A flat file or NoSQL approach would make review/approval workflow harder.

---

## Future Extensions (Not Implemented)

1. **Uncertainty Bounds**: Each quantity could have ±% confidence
2. **Chain of Custody**: Track which analyst modified what, with comment threads
3. **Baseline Tracking**: Compare to last year's emissions
4. **Calculated Fields**: Intensity ratios (kg CO2e per $ revenue, per unit produced)
5. **Materiality Analysis**: Flag records that move the needle significantly
6. **Scope 3 Supplier Data**: Indirect emissions from purchased goods/services
