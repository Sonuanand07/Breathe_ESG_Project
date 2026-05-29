"""
Data ingestion parsers for each source type.

These handle parsing raw data from SAP, Utility, and Travel sources,
normalizing them into our standard EmissionRecord format.
"""

import logging
import csv
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from apps.core.models import (
    EmissionRecord, SAPRecord, UtilityRecord, TravelRecord,
    DataSource, ScopeCategory, Unit
)

logger = logging.getLogger(__name__)


class UnitConverter:
    """
    Converts between different units used in emissions data.
    
    Different sources use different units:
    - SAP might report fuel in gallons or liters
    - Utilities use kWh or MWh
    - Travel uses miles or kilometers
    """
    
    # Conversion factors to SI base units
    CONVERSIONS = {
        # Volume conversions to liters
        'gal': 3.78541,  # US gallon to liter
        'L': 1.0,
        'gallon': 3.78541,
        'liters': 1.0,
        'm3': 1000,  # Cubic meter to liter
        
        # Energy conversions to kWh
        'kWh': 1.0,
        'MWh': 1000,
        'kWH': 1.0,  # Handle case variations
        'mWh': 1000,
        'MMBtu': 293.071,  # Million BTU to kWh
        
        # Distance conversions to km
        'km': 1.0,
        'mi': 1.60934,  # Mile to km
        'mile': 1.60934,
        'km': 1.0,
        'kilometer': 1.0,
        
        # Mass conversions to kg
        'kg': 1.0,
        'mt': 1000,  # Metric ton to kg
        'lb': 0.453592,  # Pound to kg
    }
    
    @classmethod
    def convert(cls, quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """Convert quantity from one unit to another."""
        from_unit_lower = from_unit.lower().strip()
        to_unit_lower = to_unit.lower().strip()
        
        if from_unit_lower == to_unit_lower:
            return quantity
        
        if from_unit_lower not in cls.CONVERSIONS or to_unit_lower not in cls.CONVERSIONS:
            logger.warning(f"Unknown unit conversion: {from_unit} to {to_unit}")
            return quantity
        
        conversion_factor = Decimal(cls.CONVERSIONS[from_unit_lower]) / Decimal(cls.CONVERSIONS[to_unit_lower])
        return quantity * conversion_factor


class EmissionFactors:
    """
    Standard emission factors from authoritative sources.
    
    These are simplified examples. In production, you'd pull from:
    - DEFRA/BEIS UK conversion factors
    - EPA emission factors
    - ICAO for aviation
    - Scope-specific databases
    """
    
    # Fuel emission factors (kg CO2e per liter)
    FUEL = {
        'Gasoline': Decimal('2.31'),  # kg CO2e/liter
        'Diesel': Decimal('2.68'),
        'Natural Gas': Decimal('2.04'),  # per m³
        'Propane': Decimal('1.55'),
        'Kerosene': Decimal('2.51'),
        'Jet Fuel': Decimal('2.51'),
        'LPG': Decimal('1.55'),
    }
    
    # Electricity emission factors (kg CO2e per kWh) - varies by region
    ELECTRICITY = {
        'US': Decimal('0.38'),  # Average US grid
        'EU': Decimal('0.29'),
        'UK': Decimal('0.18'),  # UK is cleaner
        'GLOBAL': Decimal('0.38'),
    }
    
    # Air travel (kg CO2e per km, including RFI multiplier)
    FLIGHT = {
        'economy': Decimal('0.09'),  # per passenger-km
        'business': Decimal('0.27'),  # Business class uses 3x space
        'first': Decimal('0.36'),
    }
    
    # Hotel (kg CO2e per night)
    HOTEL = {
        'standard': Decimal('25'),
        'luxury': Decimal('50'),
    }
    
    @classmethod
    def get_fuel_factor(cls, fuel_type: str) -> Optional[Decimal]:
        """Get emission factor for a fuel type."""
        return cls.FUEL.get(fuel_type)
    
    @classmethod
    def get_electricity_factor(cls, region: str = 'GLOBAL') -> Decimal:
        """Get emission factor for electricity by region."""
        return cls.ELECTRICITY.get(region, cls.ELECTRICITY['GLOBAL'])
    
    @classmethod
    def get_flight_factor(cls, seat_class: str = 'economy') -> Decimal:
        """Get emission factor for flights by seat class."""
        return cls.FLIGHT.get(seat_class.lower(), cls.FLIGHT['economy'])


class SAPParser:
    """
    Parse SAP export data (fuel and procurement).
    
    SAP exports come in multiple formats:
    - OData API (JSON/XML)
    - Flat file exports (CSV/XLSX)
    - IDocs (complex binary format)
    
    This implementation handles:
    - CSV exports from SAP MM (Materials Management) module
    - Common plant codes and material types
    - Unit conversions from SAP units
    """
    
    FUEL_TYPES = ['Gasoline', 'Diesel', 'Natural Gas', 'Propane', 'Kerosene', 'Jet Fuel']
    
    @staticmethod
    def parse_csv(file_content: str, client, data_source: DataSource) -> Tuple[List[Dict], List[str]]:
        """
        Parse SAP CSV export.
        
        Expected columns (example from real SAP MM export):
        - EBELN (Purchase Order)
        - EBELP (Line Item)
        - WERKS (Plant Code)
        - MATNR (Material Number)
        - MAKTX (Material Description)
        - BSTME (Unit of Measure)
        - MENGE (Quantity)
        - BUDAT (Posting Date)
        - LIFNR (Vendor Code)
        - NAME1 (Vendor Name)
        """
        records = []
        errors = []
        
        try:
            reader = csv.DictReader(file_content.split('\n'))
            
            for row_num, row in enumerate(reader, start=2):
                if not any(row.values()):  # Skip empty rows
                    continue
                
                try:
                    # Extract required fields
                    po_number = row.get('EBELN', '').strip()
                    line_item = row.get('EBELP', '').strip()
                    plant_code = row.get('WERKS', '').strip()
                    material_number = row.get('MATNR', '').strip()
                    material_desc = row.get('MAKTX', '').strip()
                    quantity_str = row.get('MENGE', '0').strip()
                    unit = row.get('BSTME', '').strip()
                    posting_date_str = row.get('BUDAT', '').strip()
                    vendor_code = row.get('LIFNR', '').strip()
                    vendor_name = row.get('NAME1', '').strip()
                    
                    # Parse quantity
                    quantity = Decimal(quantity_str.replace(',', '.'))
                    
                    # Parse date (SAP dates are typically YYYYMMDD format)
                    if posting_date_str:
                        posting_date = datetime.strptime(posting_date_str, '%Y%m%d').date()
                    else:
                        posting_date = datetime.now().date()
                    
                    # Determine if this is a fuel purchase
                    is_fuel = any(ft in material_desc.upper() for ft in SAPParser.FUEL_TYPES)
                    
                    if is_fuel:
                        # Normalize to liters
                        quantity_liters = UnitConverter.convert(quantity, unit, 'L')
                        
                        # Determine fuel type from description
                        fuel_type = 'Diesel'  # Default
                        for ft in SAPParser.FUEL_TYPES:
                            if ft.upper() in material_desc.upper():
                                fuel_type = ft
                                break
                        
                        # Calculate CO2e
                        emission_factor = EmissionFactors.get_fuel_factor(fuel_type)
                        co2e_kg = quantity_liters * emission_factor if emission_factor else Decimal('0')
                        
                        record = {
                            'client': client,
                            'data_source': data_source,
                            'scope': ScopeCategory.SCOPE_1,
                            'category': 'fleet_fuel',
                            'source_identifier': f"{po_number}-{line_item}",
                            'source_data': dict(row),
                            'quantity': quantity_liters,
                            'unit': Unit.LITER,
                            'co2e_kg': co2e_kg,
                            'transaction_date': posting_date,
                            'reporting_period_start': posting_date.replace(day=1),
                            'reporting_period_end': posting_date,
                            'location': plant_code,
                            'sap_data': {
                                'po_number': po_number,
                                'line_item': line_item,
                                'plant_code': plant_code,
                                'material_number': material_number,
                                'material_description': material_desc,
                                'fuel_type': fuel_type,
                                'vendor_code': vendor_code,
                                'vendor_name': vendor_name,
                                'original_quantity': str(quantity),
                                'original_unit': unit,
                            }
                        }
                        
                        records.append(record)
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    logger.error(f"Error parsing SAP row {row_num}: {e}")
        
        except Exception as e:
            errors.append(f"CSV parsing failed: {str(e)}")
            logger.error(f"SAP CSV parsing error: {e}")
        
        return records, errors


class UtilityParser:
    """
    Parse utility/electricity data.
    
    Sources typically provide:
    - CSV exports from utility portals
    - Meter readings (opening/closing)
    - Billing periods
    - Tariff information
    
    This handles simple CSV format with:
    - Meter ID
    - Facility name
    - Reading date
    - Consumption amount
    - Billing period
    """
    
    @staticmethod
    def parse_csv(file_content: str, client, data_source: DataSource, region: str = 'US') -> Tuple[List[Dict], List[str]]:
        """
        Parse utility CSV export.
        
        Expected columns:
        - meter_id
        - facility_name
        - utility_provider
        - billing_period_start
        - billing_period_end
        - opening_read
        - closing_read
        - consumption_kwh
        - tariff_name
        """
        records = []
        errors = []
        
        try:
            reader = csv.DictReader(file_content.split('\n'))
            
            for row_num, row in enumerate(reader, start=2):
                if not any(row.values()):
                    continue
                
                try:
                    meter_id = row.get('meter_id', '').strip()
                    facility_name = row.get('facility_name', '').strip()
                    utility_provider = row.get('utility_provider', '').strip()
                    
                    # Parse dates
                    start_str = row.get('billing_period_start', '').strip()
                    end_str = row.get('billing_period_end', '').strip()
                    
                    start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                    
                    # Parse consumption
                    consumption_kwh = Decimal(row.get('consumption_kwh', '0').strip().replace(',', '.'))
                    
                    # Calculate billing period days
                    billing_days = (end_date - start_date).days + 1
                    
                    # Get emission factor for region
                    emission_factor = EmissionFactors.get_electricity_factor(region)
                    co2e_kg = consumption_kwh * emission_factor
                    
                    record = {
                        'client': client,
                        'data_source': data_source,
                        'scope': ScopeCategory.SCOPE_2,
                        'category': 'purchased_electricity',
                        'source_identifier': f"{meter_id}-{start_date.isoformat()}",
                        'source_data': dict(row),
                        'quantity': consumption_kwh,
                        'unit': Unit.KWH,
                        'co2e_kg': co2e_kg,
                        'transaction_date': end_date,
                        'reporting_period_start': start_date,
                        'reporting_period_end': end_date,
                        'location': facility_name,
                        'utility_data': {
                            'meter_id': meter_id,
                            'facility_name': facility_name,
                            'utility_provider': utility_provider,
                            'billing_period_days': billing_days,
                            'tariff_name': row.get('tariff_name', ''),
                        }
                    }
                    
                    records.append(record)
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    logger.error(f"Error parsing utility row {row_num}: {e}")
        
        except Exception as e:
            errors.append(f"CSV parsing failed: {str(e)}")
            logger.error(f"Utility CSV parsing error: {e}")
        
        return records, errors


class TravelParser:
    """
    Parse corporate travel data from Concur/Navan.
    
    Expected fields:
    - trip_id
    - employee_id
    - travel_mode (flight, hotel, rental_car, taxi, train)
    - For flights: departure_airport, arrival_airport, seat_class
    - For hotels: hotel_name, number_of_nights
    - For ground transport: distance_km
    """
    
    # Airport code to lat/lon (simplified - in production use a proper database)
    AIRPORT_CODES = {
        'SFO': (37.7749, -122.4194),
        'LAX': (34.0522, -118.2437),
        'ORD': (41.8781, -87.6298),
        'JFK': (40.6413, -73.7781),
        'DEN': (39.8561, -104.6737),
        'SEA': (47.4502, -122.3088),
        'BOS': (42.3656, -71.0096),
        'NYC': (40.7128, -74.0060),  # General NYC
    }
    
    @staticmethod
    def calculate_distance(from_airport: str, to_airport: str) -> Optional[Decimal]:
        """
        Calculate great-circle distance between airports.
        
        In production, use a proper geocoding library or database.
        This is a simplified implementation.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        from_airport = from_airport.upper().strip()
        to_airport = to_airport.upper().strip()
        
        if from_airport not in TravelParser.AIRPORT_CODES or to_airport not in TravelParser.AIRPORT_CODES:
            return None
        
        lat1, lon1 = TravelParser.AIRPORT_CODES[from_airport]
        lat2, lon2 = TravelParser.AIRPORT_CODES[to_airport]
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return Decimal(str(distance))
    
    @staticmethod
    def parse_csv(file_content: str, client, data_source: DataSource) -> Tuple[List[Dict], List[str]]:
        """
        Parse travel CSV export.
        
        Expected columns:
        - trip_id
        - employee_id
        - travel_mode
        - departure_airport (for flights)
        - arrival_airport (for flights)
        - seat_class (for flights)
        - hotel_name (for hotels)
        - number_of_nights (for hotels)
        - distance_km (or calculate from airports)
        - cost_amount
        - cost_currency
        - expense_date
        """
        records = []
        errors = []
        
        try:
            reader = csv.DictReader(file_content.split('\n'))
            
            for row_num, row in enumerate(reader, start=2):
                if not any(row.values()):
                    continue
                
                try:
                    trip_id = row.get('trip_id', '').strip()
                    travel_mode = row.get('travel_mode', '').strip().lower()
                    expense_date_str = row.get('expense_date', '').strip()
                    
                    if not expense_date_str:
                        expense_date = datetime.now().date()
                    else:
                        expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
                    
                    # Initialize base record
                    base_record = {
                        'client': client,
                        'data_source': data_source,
                        'scope': ScopeCategory.SCOPE_3,
                        'source_identifier': trip_id,
                        'source_data': dict(row),
                        'transaction_date': expense_date,
                        'reporting_period_start': expense_date.replace(day=1),
                        'reporting_period_end': expense_date,
                        'travel_data': {}
                    }
                    
                    # Handle flights
                    if travel_mode == 'flight':
                        from_airport = row.get('departure_airport', '').strip()
                        to_airport = row.get('arrival_airport', '').strip()
                        seat_class = row.get('seat_class', 'economy').strip().lower()
                        
                        # Calculate distance if not provided
                        distance_km_str = row.get('distance_km', '').strip()
                        if distance_km_str:
                            distance_km = Decimal(distance_km_str.replace(',', '.'))
                            distance_derived = False
                        else:
                            distance_km = TravelParser.calculate_distance(from_airport, to_airport)
                            distance_derived = distance_km is not None
                        
                        if distance_km:
                            emission_factor = EmissionFactors.get_flight_factor(seat_class)
                            co2e_kg = distance_km * emission_factor
                            
                            base_record.update({
                                'category': 'business_flights',
                                'quantity': distance_km,
                                'unit': Unit.KM,
                                'co2e_kg': co2e_kg,
                                'travel_data': {
                                    'trip_id': trip_id,
                                    'from_airport': from_airport,
                                    'to_airport': to_airport,
                                    'seat_class': seat_class,
                                    'distance_derived': distance_derived,
                                }
                            })
                            records.append(base_record)
                        else:
                            errors.append(f"Row {row_num}: Could not determine flight distance from {from_airport} to {to_airport}")
                    
                    # Handle hotels
                    elif travel_mode == 'hotel':
                        nights_str = row.get('number_of_nights', '1').strip()
                        nights = int(nights_str)
                        
                        # Assume standard hotel emissions
                        emission_factor = Decimal('25')  # kg CO2e per night
                        co2e_kg = Decimal(nights) * emission_factor
                        
                        base_record.update({
                            'category': 'hotel_stays',
                            'quantity': Decimal(nights),
                            'unit': Unit.UNIT,
                            'co2e_kg': co2e_kg,
                            'travel_data': {
                                'trip_id': trip_id,
                                'hotel_name': row.get('hotel_name', ''),
                                'number_of_nights': nights,
                            }
                        })
                        records.append(base_record)
                    
                    # Handle ground transport
                    elif travel_mode in ['rental_car', 'taxi', 'train']:
                        distance_km_str = row.get('distance_km', '0').strip()
                        distance_km = Decimal(distance_km_str.replace(',', '.'))
                        
                        if distance_km > 0:
                            # Simple factor: 0.21 kg CO2e per km for car
                            emission_factor = Decimal('0.21')
                            co2e_kg = distance_km * emission_factor
                            
                            base_record.update({
                                'category': f'ground_transport_{travel_mode}',
                                'quantity': distance_km,
                                'unit': Unit.KM,
                                'co2e_kg': co2e_kg,
                                'travel_data': {
                                    'trip_id': trip_id,
                                    'travel_mode': travel_mode,
                                    'distance_km': float(distance_km),
                                }
                            })
                            records.append(base_record)
                
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    logger.error(f"Error parsing travel row {row_num}: {e}")
        
        except Exception as e:
            errors.append(f"CSV parsing failed: {str(e)}")
            logger.error(f"Travel CSV parsing error: {e}")
        
        return records, errors
