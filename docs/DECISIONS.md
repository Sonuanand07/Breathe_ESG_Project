# Design Decisions

Every nontrivial choice made during this project and the reasoning behind it.

---

## 1. SAP Data Format: CSV Flat File (Not OData API)

**Decision**: Ingest SAP data via CSV exports from the MM (Materials Management) module, not via OData API or IDoc format.

**Research**:
- **OData API**: Modern, JSON-friendly, real-time. Requires network access, OAuth setup, and rate limits.
- **IDocs**: Binary EDI format, industry standard for SAP-to-SAP, requires complex parsing libraries.
- **CSV Flat File**: Older but most reliable. Can be scheduled export from SAP, emails to a mailbox, or FTP drop.

**Why CSV**:
1. **Realistic**: Most enterprises still export SAP to Excel, not API pull. SAP on-prem installations are common in large orgs, API access often restricted.
2. **Robust**: No authentication to manage, no rate limits, no OAuth token expiration.
3. **Familiar**: Analysts can inspect the CSV before upload, verify data quality.
4. **Versioning**: Each export is a timestamped file; audit trail is explicit.

**Tradeoff**: Not real-time. Company must remember to export monthly.

**What We Handle**:
- Fuel purchases from MENGE (quantity) + BSTME (unit) + MAKTX (description)
- Plant codes (WERKS) for facility tracking
- Vendor names for reconciliation
- Dates in SAP format (YYYYMMDD)
- Currency is inferred or ignored (fuel quantities in liters matter, not price)

**What We Ignore**:
- Procurement of non-fuel materials (raw materials, equipment) - not emissions-related
- Depreciation, allocation, or internal cost center transfers
- Multiple ledger entries for the same PO (we take the last/final entry)

---

## 2. Utility Data Format: CSV Portal Export (Not PDF Parsing)

**Decision**: Ingest utility data from CSV exports provided by facilities teams, not parse PDFs.

**Research**:
- **PDF Bill Parsing**: Possible with libraries like pdfplumber, but bills vary by utility (PG&E, Duke Energy, etc.) and often require ML/OCR.
- **Utility API**: Some utilities offer APIs (e.g., some municipal utilities, some commercial platforms), but access requires special accounts.
- **Portal CSV**: Most utilities allow downloading billing history as CSV (PG&E, Duke, Ameren, etc.).

**Why CSV Portal Export**:
1. **Structured**: Meter readings are already numeric, no OCR errors.
2. **Historical**: Portal exports include 12-24 months of history in one download.
3. **Universally Available**: Every utility I researched offers CSV download capability.
4. **Testable**: We can publish sample CSVs for training.

**Billing Period Complexity**:
- Utilities read meters on fixed schedules (e.g., every 32-35 days), not on calendar months.
- Model stores `billing_period_start`, `billing_period_end`, and `billing_cycle_days`.
- Analysts can see "this period had 35 days, consumption should be annualized" without our code making assumptions.

**What We Handle**:
- Meter ID and facility name for multi-site companies
- Opening read, closing read, and consumption (one-shot, not estimated)
- Billing period (non-calendar alignment)
- Tariff name (for later analysis of rate structures)
- Transmission loss factor (typically 1.05-1.08)

**What We Ignore**:
- Demand charges, reactive power, power factor (scope isn't technical electricity analysis)
- Distributed generation / net metering (out of scope for MVP)
- Water consumption (not emissions-related without wastewater treatment modeling)

---

## 3. Corporate Travel: Concur/Navan-Like JSON API (Simulated with CSV)

**Decision**: Model the ingestion after modern travel platforms (Concur API, Navan API) but for MVP, accept CSV export.

**Research**:
- **Concur API**: Actual integration possible but requires legal agreements with Concur and setup time.
- **Navan API**: Similar, and Navan is newer/simpler, but still requires partnership.
- **CSV Export**: Both Concur and Navan allow CSV export of trip history.

**Why This Design**:
1. **Future-Proof**: Code is designed to handle JSON trip objects (as Concur API returns), not just CSV columns. Can pivot to API pull later.
2. **Realistic Data**: API response format includes fields like `trip_id`, `employee_id`, `departure_airport`, `seat_class`.
3. **Distance Calculation**: If airport codes are provided but distance isn't, we calculate using great-circle formula.
4. **Categorization**: Different modes (flight, hotel, rental car) have different emission factors.

**What We Handle**:
- Flights: departure/arrival airports (IATA codes), seat class, distance
- Hotels: nights stayed, assumes standard emission factor
- Ground transport: rental cars, taxis, trains (by distance)
- Cost as secondary validation (doesn't directly calculate emissions, but present for reconciliation)

**What We Ignore**:
- Meal per diem (not emissions)
- Incidental expenses (not emissions)
- Employee names (privacy - we store employee_id only)
- Multi-leg trips simplified (each flight segment becomes one record)
- Emissions from hotels post-stay employee activities

**Distance Derivation**:
- If distance is provided, use it
- If not, calculate from airport codes using simplified great-circle distance
- Mark record as `distance_derived: true` for audit trail
- This is critical because "I flew SFO → LAX" needs distance to calculate emissions

---

## 4. Review Workflow: Analyst Must Explicitly Approve

**Decision**: Records start as PENDING, analyst must approve or reject. No auto-approval.

**Rationale**:
- Auditors require "someone with authority signed off on this number"
- Data governance: allow analyst to catch obvious errors (misaligned units, wrong facility)
- Compliance: timestamps of approval + approved_by user ensure accountability

**States**:
- **PENDING**: Just ingested, awaiting review
- **FLAGGED**: Analyst has concerns, needs further investigation
- **APPROVED**: Ready to report to auditors
- **REJECTED**: This record shouldn't be in the final report

**Why Not Auto-Flag for Issues?**:
- We could mark outliers (e.g., electricity usage 5x normal) automatically
- But domain experts might know these are legitimate (facility expansion, cold weather heating)
- Better to surface them and let analyst decide

---

## 5. Multi-Tenancy: Client-Level, Not Organization/Department

**Decision**: Top-level tenant is Client (enterprise company), not Organization (department within company) or Plant (individual facility).

**Why**:
- PM said "onboarding a new enterprise client"
- Breathe ESG's pricing model likely per-client, not per-facility
- Regulatory reporting is at company level (e.g., SEC climate disclosure for entire corporation)
- Different clients have different emission factors, audit requirements, Scope 3 policies

**If This Were Extended**:
- Could add Organization model (departments within a client)
- Could add Facility model (plants/sites within an organization)
- But MVP keeps scope to Client level

---

## 6. Scope 1/2/3 As Required Field

**Decision**: Every record must have a scope. Not optional.

**Why**:
- GHG Protocol requires scope categorization for regulatory compliance
- Different scopes have different audit scrutiny
- Scope 3 (travel) might be optional for some companies; Scope 1 (fleet) is not

**Mapping**:
- SAP fuel → Scope 1 (company-owned/controlled fleet)
- Utility electricity → Scope 2 (purchased energy)
- Travel → Scope 3 (other indirect - even though company pays, employees are third-party actors)

---

## 7. Source Data Stored as Immutable JSON

**Decision**: Original source data (before parsing) stored in a JSON field on EmissionRecord.

**Why**:
- Audit trail: "if you dispute this record, here's the raw line item"
- Backward compatible: if we discover a parsing bug in 2026, we can reprocess
- Transparency: analysts can inspect original data without asking for re-export

**Example**:
```json
{
  "EBELN": "4600012345",
  "MAKTX": "DIESEL FUEL",
  "MENGE": "1500",
  "BSTME": "L"
}
```

---

## 8. Unit Conversion Tracked Explicitly

**Decision**: Store both original unit and normalized unit, plus the conversion factor applied.

**Why**:
- Transparency: if analyst questions "why is this in liters not gallons?", we can explain
- Reproducibility: the exact conversion factor used is logged
- Debugging: if we discover a conversion is wrong, we can trace through audit log

---

## 9. REST API Over GraphQL

**Decision**: Use Django REST Framework (DRF), not GraphQL.

**Why**:
- **Simpler**: Analysts aren't writing complex nested queries; they're mostly filtering a list
- **Caching**: REST endpoints are easier to cache (GET /records?status=pending)
- **Familiarity**: More analysts know REST than GraphQL

---

## 10. React for Frontend (Not Vue, Not Static HTML)

**Decision**: Single-page app in React for analyst dashboard.

**Why**:
1. **Interactivity**: Analyst needs responsive filtering, quick approval/reject without page reloads
2. **State Management**: Zustand for simple global state (selected client, auth token)
3. **Component Reusability**: RecordCard, StatusBadge, FilterPanel used multiple places
4. **Real-time Feedback**: Approve a record, see status change immediately

---

## 11. PostgreSQL Over SQLite

**Decision**: Use PostgreSQL for production, SQLite optional for dev.

**Why**:
- **Transactions**: Ingestion must be atomic. PostgreSQL handles concurrent uploads better.
- **Indexing**: Complex queries on dates, statuses benefit from PostgreSQL indexes
- **Multi-user**: Multiple analysts simultaneous access
- **Deployment**: Managed PostgreSQL (Render, Fly, Heroku) scales easily

---

## 12. Emission Factor Versioning Not Implemented

**Decision**: Hard-coded emission factors in `EmissionFactors` class for MVP.

**Why Not Implemented**:
- Scope creep: managing factor revisions, audit trail per factor, requires more tables
- Use Case: Most companies don't change factors mid-year (they're locked for annual reporting)
- Data Source: Where do updated factors come from? Industry publishes annually.

**If Extended**:
```python
EmissionFactorVersion:
  - id
  - name ("DEFRA 2023", "EPA eGRID 2023")
  - fuel_type, value, unit
  - effective_date
  - archived_at
```

---

## 13. No Role-Based Access Control (RBAC) in MVP

**Decision**: All authenticated users can approve/reject/flag records. No role hierarchy.

**Why Not Implemented**:
- PM didn't specify: "only ESG Manager can approve", "Analyst can only flag"
- Most companies don't have complex roles (it's small team doing ESG initially)
- Overhead: would require permissions table, group membership, endpoint guards

**If Extended**:
```python
class RoleChoices:
  VIEWER = 'viewer'  # read-only
  ANALYST = 'analyst'  # approve/reject/flag
  MANAGER = 'manager'  # all, plus export for audit
  ADMIN = 'admin'  # all, plus user management
```

---

## 14. No Encryption of Sensitive Data in MVP

**Decision**: DataSource.configuration stored as plain JSON, no field-level encryption.

**Why Not Implemented**:
- Django-encrypted-model-fields adds complexity
- Demo/MVP on Render can use HTTPS (data in transit encrypted)
- Production would require:
  - Encrypted DB fields
  - Secrets manager (AWS Secrets, HashiCorp Vault)
  - Key rotation policy

---

## 15. Ingestion is Synchronous (Not Async)

**Decision**: File upload processing happens immediately, blocks until complete.

**Why Not Async (Celery/Redis)**:
- Small files (100-500 records) process in <1 second
- Analyst gets immediate feedback ("500 records imported, 0 failed")
- Avoids Redis dependency for MVP

**If Extended** (10k+ record files):
```python
# Queue job, return job_id immediately
ingestion_job = IngestionJob.objects.create(...)
process_ingestion_job.delay(job_id)  # Celery task
# Analyst polls for completion or gets webhook
```

---

## 16. No Soft Delete for EmissionRecords

**Decision**: Once approved and locked for audit, records cannot be deleted.

**Why**:
- Audit requirement: "we reported this number to SEC"
- If a mistake is discovered, we add a correcting entry, not delete
- Immutability builds trust with auditors

---

## 17. Quality Score Not Implemented (Placeholder)

**Decision**: Every record defaults to quality_score = 100. No auto-degradation logic.

**Why Not Implemented**:
- Would require domain rules: "if quantity > last month × 2, score = 80"
- Risks false positives (e.g., new equipment installation doubles fuel)
- Analyst eyeballs the numbers and flags manually if suspicious

**If Extended**:
```python
quality_score = 100
if quantity > threshold:
    quality_score -= 20  # Outlier
if unit_conversion_applied:
    quality_score -= 5  # Possible rounding error
```

---

## Questions for PM (If This Were Real)

1. **Real-Time vs Batch?** Should ingestion be real-time (API webhooks from SAP/Concur) or monthly batch?
2. **Scope 3 Boundary?** Do we include employee commute? Upstream supply chain?
3. **Factor Updates?** When electricity grid factors change (annually), how are historical records updated?
4. **Export Format?** Auditors want what format? Excel? XBRL? Plain CSV?
5. **Concurrent Approval?** Can two analysts approve the same record simultaneously? What if they disagree?
6. **Multi-Year Baseline?** Compare year-over-year or just report current year?
7. **Materiality Threshold?** Below what CO2e value do we not require approval?
8. **Employee Privacy?** Travel data includes employee_id. Can employees see their own trips?
9. **Third-Party Verification?** Does Breathe ESG collect data, or does the client collect and we just review?
10. **Cost Allocation?** If a hotel stay is split between business and personal, how is that handled?

---

## Principles Applied

1. **Data Governance > Feature Richness**
   - A smaller app that auditors trust beats a feature-rich app they question

2. **Explicit > Implicit**
   - Better to require an analyst to approve than auto-approve and hope nothing breaks

3. **Transparent > Clever**
   - Conversion factors are visible, not hidden in a library
   - Original data stored alongside calculations

4. **Realistic > Idealistic**
   - CSV exports are real. API integrations are aspirational.
   - Analyst review is necessary. Auto-detection is insufficient.

5. **Scalable > Optimized**
   - Model supports 1M records per client eventually
   - Query performance not optimized for edge cases in MVP
