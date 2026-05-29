# Sample Data Files

This directory contains sample CSV files for testing data ingestion.

## SAP Data (sap_sample.csv)

Expected columns for SAP fuel and procurement exports:

```csv
EBELN,EBELP,WERKS,MATNR,MAKTX,BSTME,MENGE,BUDAT,LIFNR,NAME1
4600012345,00010,1000,MAT-001,DIESEL FUEL - 2-D,L,1500,20240115,200005,ABC Oil Company
4600012345,00020,1000,MAT-002,GASOLINE PREMIUM,L,500,20240115,200005,ABC Oil Company
4600012346,00010,2000,MAT-001,DIESEL FUEL - 2-D,GAL,2000,20240120,200010,Fuel Corp
4600012347,00010,1500,MAT-003,JET FUEL - JP-8,L,10000,20240125,200015,Aviation Fuels Inc
4600012348,00010,3000,MAT-004,NATURAL GAS,KG,5000,20240128,200020,Gas Supplier Inc
```

**Column Descriptions**:
- EBELN: Purchase Order Number
- EBELP: Line Item Number
- WERKS: Plant Code (facility identifier)
- MATNR: Material Number
- MAKTX: Material Description (used to identify fuel type)
- BSTME: Unit of Measure (L, GAL, KG, etc.)
- MENGE: Quantity
- BUDAT: Posting Date (YYYYMMDD format)
- LIFNR: Vendor/Supplier Code
- NAME1: Vendor/Supplier Name

---

## Utility Data (utility_sample.csv)

Expected columns for utility portal CSV exports:

```csv
meter_id,facility_name,utility_provider,billing_period_start,billing_period_end,opening_read,closing_read,consumption_kwh,tariff_name,read_type
MTR-001-SF,San Francisco HQ,PG&E,2024-01-12,2024-02-16,45237,47832,2595,A-10 General Service,Actual
MTR-002-LA,Los Angeles Warehouse,Southern California Edison,2024-01-15,2024-02-14,128456,131245,2789,TOU-GS1B,Actual
MTR-003-DEN,Denver Office,Xcel Energy,2024-01-10,2024-02-10,98765,99543,778,Commercial Standard,Estimated
MTR-004-CHI,Chicago Distribution,ComEd,2024-01-08,2024-02-08,267890,275432,7542,Business Delivery,Actual
MTR-005-BOS,Boston Research Center,Eversource,2024-01-15,2024-02-15,156234,159876,3642,General Service,Actual
```

**Column Descriptions**:
- meter_id: Unique meter identifier
- facility_name: Human-readable facility name
- utility_provider: Name of utility company
- billing_period_start: Start date of billing period (YYYY-MM-DD)
- billing_period_end: End date of billing period (YYYY-MM-DD)
- opening_read: Opening meter reading (kWh)
- closing_read: Closing meter reading (kWh)
- consumption_kwh: Calculated consumption (closing - opening)
- tariff_name: Rate schedule/tariff type
- read_type: "Actual" or "Estimated"

---

## Corporate Travel Data (travel_sample.csv)

Expected columns for travel platform exports (Concur/Navan style):

```csv
trip_id,employee_id,travel_mode,departure_airport,arrival_airport,distance_km,seat_class,hotel_name,number_of_nights,cost_amount,cost_currency,expense_date
TRIP-001,EMP-100,flight,SFO,JFK,4160,economy,,,,450,USD,2024-01-15
TRIP-002,EMP-100,hotel,,,,,Marriott NYC,3,,600,USD,2024-01-16
TRIP-003,EMP-102,flight,LAX,ORD,3125,business,,,,1200,USD,2024-02-01
TRIP-004,EMP-103,rental_car,,,280,economy,,,,150,USD,2024-02-05
TRIP-005,EMP-104,train,,,400,economy,,,,80,USD,2024-02-10
TRIP-006,EMP-105,flight,SEA,DEN,,economy,,,,320,USD,2024-02-12
TRIP-007,EMP-106,flight,BOS,LAX,4160,business,,,,2400,USD,2024-02-18
TRIP-008,EMP-107,hotel,,,,,Hyatt Chicago,2,,400,USD,2024-02-20
```

**Column Descriptions**:
- trip_id: Unique trip identifier
- employee_id: Employee ID (for tracking, no names)
- travel_mode: "flight", "hotel", "rental_car", "taxi", "train"
- departure_airport: IATA airport code (for flights)
- arrival_airport: IATA airport code (for flights)
- distance_km: Distance in kilometers (optional for flights, required for ground transport)
- seat_class: "economy", "business", "first" (flights only)
- hotel_name: Name of hotel (hotels only)
- number_of_nights: Number of nights stayed (hotels only)
- cost_amount: Cost in currency
- cost_currency: Currency code (USD, EUR, etc.)
- expense_date: Date of expense (YYYY-MM-DD)

**Notes**:
- For flights without distance_km, system calculates from airport codes
- Seat class defaults to "economy" if not specified
- Hotel nights use standard emission factor (25 kg CO2/night)
- Ground transport emissions calculated as distance × mode-specific factor

---

## How to Test

1. **Start the application**:
   ```bash
   docker-compose up
   ```

2. **Access the dashboard**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Admin: http://localhost:8000/admin (username: admin, password: admin)

3. **Create a test client** (via Django admin):
   - Name: "Test Company Inc"
   - Legal Entity ID: "12345-ABC"
   - Country: "US"
   - Fiscal Year Start: "2024-01-01"

4. **Register data sources** (via API or admin):
   ```
   POST /api/data-sources/
   {
     "client": "<client_id>",
     "source_type": "sap",
     "name": "SAP ERP Prod",
     "configuration": {}
   }
   ```

5. **Upload sample files**:
   - Copy one of the CSV samples above
   - Upload via dashboard "Upload Data" page
   - Or use API:
     ```bash
     curl -X POST http://localhost:8000/api/ingestion/ingest-sap/ \
       -H "Authorization: Token <your_token>" \
       -F "file=@sap_sample.csv" \
       -F "client_id=<client_id>" \
       -F "data_source_id=<source_id>"
     ```

6. **Review records**:
   - Records appear in dashboard
   - Click to view details
   - Approve or flag for review

---

## Notes

- All dates should be in YYYY-MM-DD format (except SAP BUDAT which is YYYYMMDD)
- Quantities can use decimal (1500.5)
- Currency is optional for travel data (used for reconciliation only)
- System auto-calculates CO2e based on quantity, unit, and emission factors
- Analyst must approve records before they're locked for audit
