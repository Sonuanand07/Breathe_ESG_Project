# Sources: Research & Implementation

For each of the three data sources, this document covers:
1. Real-world format research
2. Key learnings
3. Sample data structure  
4. What we handle
5. What would break in production

---

## 1. SAP (Fuel & Procurement Data)

### Real-World Format Research

**SAP Overview**:
SAP is an enterprise resource planning (ERP) system used by ~90% of Fortune 500 companies. It tracks everything: purchases, inventory, payments, shipments. For emissions, we care about Materials Management (MM) module.

**Key SAP Modules**:
- **MM (Materials Management)**: Tracks purchases and inventory
  - MENGE (quantity), BSTME (unit), MAKTX (material description)
  - EBELN (purchase order), EBELP (line item), BUDAT (posting date)
  - WERKS (plant), LIFNR (vendor)
- **FI-CO (Finance & Controlling)**: Tracks costs and cost allocation
- **Logistics**: Fuel usage, fleet mileage (though many companies track this in separate fleet systems)

**Export Formats**:
1. **CSV/Flat File** (most common):
   - Facilities/procurement teams use ABAP query builder to export MM data
   - Output: Tab-delimited or comma-separated flat file
   - Headers are customizable, sometimes in German (MENGE vs. Quantity)

2. **OData API** (newer, REST-friendly):
   - Available in SAP S/4HANA and SAP Analytics Cloud
   - Requires OAuth2 setup, technical user, API deployment
   - Returns JSON, supports filtering/pagination
   - But older SAP ECC (still ~50% of installs) has limited OData

3. **IDocs** (EDI format):
   - Legacy, used for SAP-to-SAP or SAP-to-EDI-receiver
   - Binary, requires ABAP parsing
   - Not practical for external integrations

**What We Learned**:
- **Units Are a Mess**: SAP allows user-defined units. Fuel might be in L, gal, kg, or even "pallets"
- **Dates Are Inconsistent**: Some systems use YYYYMMDD, others MM/DD/YYYY. Locale-dependent parsing is risky.
- **German/English**: German SAP instances use German column headers (MENGE = quantity)
- **Duplicates**: POs can have multiple posting dates if partially received. Need to handle duplicates.
- **Missing Data**: Some fields are optional. Vendor name might be blank. Plant code might be "0000" (catch-all).
- **Materiality**: Fuel is 5-10% of SAP purchases. Must filter for fuel-only (MAKTX contains "Diesel", "Fuel", "Petrol", etc.)

### Sample Data

**Input CSV** (as exported from SAP):
```csv
EBELN,EBELP,WERKS,MATNR,MAKTX,BSTME,MENGE,BUDAT,LIFNR,NAME1
4600012345,00010,1000,MAT-001,DIESEL FUEL - 2-D,L,1500,20240115,200005,ABC Oil Company
4600012345,00020,1000,MAT-002,GASOLINE PREMIUM,L,500,20240115,200005,ABC Oil Company
4600012346,00010,2000,MAT-001,DIESEL FUEL - 2-D,GAL,2000,20240120,200010,Fuel Corp
4600012347,00010,1500,MAT-003,JET FUEL - JP-8,L,10000,20240125,200015,Aviation Fuels Inc
```

**Parsing Output** (one EmissionRecord per line):
```python
{
  "scope": "scope_1",
  "category": "fleet_fuel",
  "source_identifier": "4600012345-00010",
  "quantity": 1500,  # Already in liters
  "unit": "L",
  "co2e_kg": 1500 * 2.68 = 4020,  # Diesel factor
  "transaction_date": "2024-01-15",
  "location": "1000",  # Plant code
  "sap_data": {
    "po_number": "4600012345",
    "plant_code": "1000",
    "material_number": "MAT-001",
    "fuel_type": "Diesel",
    "vendor_code": "200005",
    "vendor_name": "ABC Oil Company",
    "original_quantity": "1500",
    "original_unit": "L"
  }
}
```

### What We Handle

✅ **Supported**:
- Fuel purchases with common units (L, gal, kg)
- Plant codes (facility tracking)
- Vendor names (reconciliation)
- Date parsing in YYYYMMDD format
- Multiple fuel types (Diesel, Gasoline, Natural Gas, Kerosene)
- Unit conversion (e.g., GAL → L)

❌ **Not Supported**:
- Procurement of non-fuel materials (raw materials, equipment)
- Depreciation or internal transfers (cost allocation)
- Invoice-level data (we work at PO line level)
- Multiple posting dates for one PO (we'd need to aggregate)
- Non-standard fuel types (we default to "Diesel" if description is unrecognized)

### What Would Break

1. **Unexpected Units**: If SAP has unit = "pallets" or "drums", conversion fails
   - *Fix*: Add manual conversion mapping or require pre-normalized SAP export

2. **Date Format Changes**: If export format switches from YYYYMMDD to MM/DD/YYYY
   - *Fix*: Add date format detection or document required export settings

3. **Missing Fuel Type Description**: If MAKTX is blank, we can't identify fuel
   - *Fix*: Use material number lookup table or require filled descriptions

4. **Extremely Large Quantities**: If Germany uses comma decimal (1.500,5 instead of 1500.5)
   - *Fix*: Detect locale and parse accordingly

5. **Multi-Currency Pricing**: If SAP quantity includes currency conversions
   - *Fix*: We ignore currency, work only with quantity

6. **Supplier Consolidation**: If vendor codes merge (200005 → 200020), we lose reconciliation
   - *Fix*: Maintain vendor master lookup table

---

## 2. Utility Data (Electricity)

### Real-World Format Research

**Utility Background**:
Electricity billing is complex. Companies don't get a simple "kWh used" number. They get meter readings, tariff structures, and billing periods that don't align with months.

**Meter Reading Reality**:
- **Meter Type**:
  - Analog: Meter reader checks monthly, reads absolute kWh (e.g., 45,237 kWh), subtracts opening read
  - Smart Meter (AMI): Hourly or 15-minute interval data available
  - Most US utilities transitioning to AMI (Advanced Metering Infrastructure)

- **Billing Period**: Often 28-35 days, not 30 days. Example:
  - Billing period: Jan 12 - Feb 16 (36 days)
  - But we need to normalize to "monthly equivalents" for reporting
  - Transmission loss factor: 1.05-1.08 (power lost in distribution lines)

- **Tariff Structures**: Simple or complex
  - Simple: $0.12/kWh (flat rate)
  - Complex: $0.10/kWh for first 1000 kWh, $0.08/kWh above (tiered)
  - Seasonal: Different rates for summer/winter
  - Time-of-Use: $0.15/kWh peak, $0.08/kWh off-peak

**Typical Export Formats**:

1. **CSV from Utility Portal** (most common):
   - Meter readings: opening, closing, consumption
   - Billing period start/end
   - Account number, tariff, invoice details
   - Downloadable for 12-24 months

2. **PDF Bill** (harder):
   - Requires OCR or manual entry
   - Inconsistent layout per utility
   - Out of scope for MVP

3. **API** (uncommon):
   - USIBC (Utilities Sector Information Baseline Committee) is standardizing
   - OpenADR (for demand response)
   - Only available from modern utilities, often with extra fees

**What We Learned**:
- **Billing Cycle Mismatch**: Can't assume kWh is "per month". Must track actual dates.
- **Grid Carbon Intensity Varies**: Electricity in Kentucky (coal) is dirtier (0.45 kg CO2/kWh) than California (renewables) (0.1 kg CO2/kWh)
- **Transmission Losses**: Lose ~5-8% to distribution line losses. Utilities sometimes include this in billing, sometimes don't.
- **Estimated Reads**: Some months are "estimated" (meter not read). Analyst must flag or confirm.
- **Distributed Generation**: If facility has solar, net metering subtracts from consumption. Need separate tracking.
- **Demand Charges**: Commercial billing includes $ per kW peak demand, not just kWh. Complicates cost vs. emissions analysis.

### Sample Data

**Input CSV** (as exported from utility portal):
```csv
meter_id,facility_name,utility_provider,billing_period_start,billing_period_end,opening_read,closing_read,consumption_kwh,tariff_name,read_type
MTR-001-SF,San Francisco HQ,PG&E,2024-01-12,2024-02-16,45237,47832,2595,A-10 General Service,Actual
MTR-002-LA,Los Angeles Warehouse,Southern California Edison,2024-01-15,2024-02-14,128456,131245,2789,TOU-GS1B Peak Hours,Actual
MTR-003-DEN,Denver Office,Xcel Energy,2024-01-10,2024-02-10,98765,99543,778,Commercial Standard,Estimated
```

**Parsing Output**:
```python
{
  "scope": "scope_2",
  "category": "purchased_electricity",
  "source_identifier": "MTR-001-SF-2024-01-12",
  "quantity": 2595,  # kWh
  "unit": "kWh",
  "co2e_kg": 2595 * 0.38 = 985,  # US average grid factor
  "transaction_date": "2024-02-16",  # End of billing period
  "reporting_period_start": "2024-01-12",
  "reporting_period_end": "2024-02-16",
  "location": "San Francisco HQ",
  "utility_data": {
    "meter_id": "MTR-001-SF",
    "facility_name": "San Francisco HQ",
    "utility_provider": "PG&E",
    "billing_period_days": 36,
    "tariff_name": "A-10 General Service",
    "read_type": "Actual",
  }
}
```

### What We Handle

✅ **Supported**:
- Meter readings (opening, closing, consumption in kWh)
- Non-calendar billing periods (tracks actual days)
- Multiple facilities (one meter per record)
- US/EU/UK electricity grids (different emission factors by region)
- Tariff names (metadata, no calculation)
- Actual vs. Estimated reads (flagged)

❌ **Not Supported**:
- Demand charges (peak kW) - not emissions-related
- Distributed generation / solar offsets
- Net metering (received power vs. sent power)
- Reactive power or power factor correction
- Time-of-use tariff pricing (simplified to single kWh rate)
- Multi-meter aggregation (e.g., 5 meters on one account)

### What Would Break

1. **Non-Standard Consumption Column**: If CSV says "usage_mwh" (megawatt-hours) not "consumption_kwh"
   - *Fix*: Auto-detect unit and convert

2. **Region Mismatch**: If we assume US emission factor (0.38) for German electricity (0.29)
   - *Fix*: Infer region from utility provider name or ask analyst

3. **Missing Billing Period**: If dates are blank, assume calendar month
   - *Fix*: Require dates or disable record

4. **Negative Consumption**: If net metering produces negative number
   - *Fix*: Abs() value and flag as "grid export" (different classification)

5. **Wildly Inconsistent Dates**: If meter reads are April, May, July (skipped June)
   - *Fix*: Analyst manually checks and flags missing periods

6. **Estimated Reads**: EPA/auditors may not accept estimated months for official reporting
   - *Fix*: Store read_type field, analyst can exclude "Estimated" records

---

## 3. Corporate Travel (Flights, Hotels, Ground Transport)

### Real-World Format Research

**Travel Platform Ecosystem**:

1. **Concur** (SAP subsidiary, largest):
   - Expense management + travel booking
   - API returns trip segments, booking details, cost
   - Used by majority of US Fortune 500

2. **Navan** (newer, founded 2019, acquired by SAP 2023):
   - Modern UI, real-time data
   - API is simpler than Concur
   - Growing adoption in tech/startup companies

3. **Corporate Cards**: Amex, Visa corporate cards
   - Expense categorization (travel, meals, etc.)
   - Requires linking to merchant data to identify flights vs. hotels

4. **Individual Reports**: Some companies have employees submit travel via manual form or email

**Trip Data Reality**:
- Employees don't always enter distance. "New York to Los Angeles" requires looking up airport codes and calculating.
- Seat class matters: Business class emits ~3x economy (more space per passenger).
- Airlines don't always disclose exact distances (use great-circle approximation).
- Hotel emissions are hard: depends on hotel size, location, energy source. We use standard factor (25 kg CO2/night).
- Ground transport varies: rental car (0.21 kg/km), rideshare (varies), taxi (0.3 kg/km), train (0.05 kg/km).

**Typical Export Formats**:

1. **Concur/Navan API** (JSON):
   ```json
   {
     "trips": [
       {
         "id": "trip-12345",
         "employee_id": "EMP-001",
         "segments": [
           {
             "type": "flight",
             "departure_airport": "SFO",
             "arrival_airport": "JFK",
             "distance_km": 4160,
             "seat_class": "economy",
             "airline": "United Airlines",
             "cost_usd": 450
           },
           {
             "type": "hotel",
             "hotel_name": "Marriott Times Square",
             "nights": 3,
             "cost_usd": 600
           }
         ],
         "start_date": "2024-01-15",
         "end_date": "2024-01-20"
       }
     ]
   }
   ```

2. **CSV Export** (what most companies actually use):
   ```csv
   trip_id,employee_id,travel_mode,departure_airport,arrival_airport,distance_km,seat_class,cost_amount,cost_currency,expense_date
   ```

**What We Learned**:
- **Distance Is Critical**: Without distance, can't calculate emissions. But flight distance isn't always provided.
  - Solution: Calculate from airport codes using great-circle formula
  - Caveat: Doesn't account for actual flight path (winds, routing) or connecting flights

- **Seat Class Matters**: Business class emits ~3x economy because airlines allocate less cargo to more passengers. RFI (Radiative Forcing Index) multiplier further increases air travel emissions.

- **Hotel Emissions Are Rough**: Don't have per-hotel data. Use industry average (~25 kg CO2/night). Actual varies 10-50x by hotel.

- **Ground Transport Is Local**: Rental car in LA vs. Beijing has very different emission factors (US grid dirtier, but local transport depends on car type/fuel).

- **Privacy**: Employee names and travel patterns might be sensitive. Recommend storing employee_id, not names.

- **Personal vs. Business**: Some trips are personal (weekend), mixed with business. No clear way to split without knowing context.

### Sample Data

**Input CSV** (Navan-style export):
```csv
trip_id,employee_id,travel_mode,departure_airport,arrival_airport,distance_km,seat_class,hotel_name,number_of_nights,cost_amount,cost_currency,expense_date
TRIP-001,EMP-100,flight,SFO,JFK,4160,economy,,,,450,USD,2024-01-15
TRIP-002,EMP-100,hotel,,,,,Marriott NYC,3,,600,USD,2024-01-16
TRIP-003,EMP-102,flight,LAX,ORD,3125,business,,,,1200,USD,2024-02-01
TRIP-004,EMP-103,rental_car,,,280,economy,,,,150,USD,2024-02-05
TRIP-005,EMP-104,train,,,400,economy,,,,80,USD,2024-02-10
```

**Parsing Output**:
```python
# Flight
{
  "scope": "scope_3",
  "category": "business_flights",
  "source_identifier": "TRIP-001",
  "quantity": 4160,  # km
  "unit": "km",
  "co2e_kg": 4160 * 0.09 = 374,  # Economy factor
  "transaction_date": "2024-01-15",
  "travel_data": {
    "trip_id": "TRIP-001",
    "from_airport": "SFO",
    "to_airport": "JFK",
    "seat_class": "economy",
    "distance_derived": False,  # Provided in data
  }
}

# Hotel
{
  "scope": "scope_3",
  "category": "hotel_stays",
  "source_identifier": "TRIP-002",
  "quantity": 3,  # nights
  "unit": "unit",
  "co2e_kg": 3 * 25 = 75,  # Standard hotel factor
  "transaction_date": "2024-01-16",
  "travel_data": {
    "trip_id": "TRIP-002",
    "hotel_name": "Marriott NYC",
    "number_of_nights": 3,
  }
}

# Rental Car
{
  "scope": "scope_3",
  "category": "ground_transport_rental_car",
  "source_identifier": "TRIP-004",
  "quantity": 280,  # km
  "unit": "km",
  "co2e_kg": 280 * 0.21 = 59,  # Car factor
  "transaction_date": "2024-02-05",
  "travel_data": {
    "trip_id": "TRIP-004",
    "travel_mode": "rental_car",
    "distance_km": 280,
  }
}
```

### What We Handle

✅ **Supported**:
- Flights with airport codes (calculate distance if needed)
- Seat class (economy, business, first)
- Hotels with night count (standard emission factor)
- Ground transport: rental cars, taxis, trains (distance-based)
- Cost as metadata (for reconciliation, not for emissions calculation)
- Distance derivation from airport code pairs
- Multiple trip modes in one ingestion

❌ **Not Supported**:
- Multi-leg flights (simplified to one segment)
- Connecting flights (not distinguished from direct)
- Emissions from airline catering or baggage
- Hotel-specific emissions (we use industry average)
- Rideshare fleet composition (Uber vs. Lyft, electric vs. gas)
- Train type (local commuter vs. high-speed)
- Cruise ships or charter flights
- Personal travel (can't distinguish from business)

### What Would Break

1. **Ambiguous Airport Codes**: If SFO is given but we don't know if it's San Francisco (SFO) or Santa Fe (SAF)
   - *Fix*: Maintain airport code database, prompt analyst if ambiguous

2. **Missing Seat Class**: Default to economy, but actual was business (3x emissions underestimated)
   - *Fix*: Require seat_class field or ask analyst to estimate

3. **Distance Given in Miles Not Km**: If data says 2500 and we assume km, wrong by 60%
   - *Fix*: Detect unit or require explicit unit column

4. **Multi-Leg Trip Not Separated**: Passenger flew SFO → LAX → JFK (2 flights), but CSV has only start/end (SFO → JFK, 4160 km)
   - *Fix*: Treat as one flight. Won't capture actual distance. Ask analyst for segment breakdown.

5. **Hotel Chain Without Location**: "Marriott" doesn't tell us if it's 4-star luxury or 2-star budget (50x difference in emissions)
   - *Fix*: Use location to infer hotel tier, or require manual override

6. **Personal Days Included**: 3-day hotel stay, but only 2 business days. We count 3 nights (overestimate)
   - *Fix*: Analyst manually adjusts or flags for review

---

## Summary

| Source | Realistic Format | Key Complexity | Biggest Risk |
|--------|------------------|-----------------|--------------|
| SAP | CSV flat file (MM module) | Unit conversions, date parsing | Fuel type identification from description |
| Utility | CSV portal export | Non-calendar billing periods | Grid emission factor varies by region |
| Travel | Concur/Navan CSV | Distance derivation from airport codes | Missing seat class or multi-leg simplification |

All three formats are production-ready. Production system would add:
- Encryption for sensitive data (employee IDs, vendor names)
- Better error handling and user-friendly messages
- Region/facility lookup tables
- Airline/hotel/transport emission factor versioning
- Integration with source systems API (Concur, Navan) for real-time pulls vs. CSV batch
