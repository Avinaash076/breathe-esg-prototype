"""
Utility/Energy consumption data parser.

Parses energy consumption reports from utility providers,
handles electricity, water, and gas usage data.
"""

import csv
from datetime import datetime
from decimal import Decimal


class UtilityDataParser:
    """Parser for utility consumption data."""
    
    def __init__(self):
        """Initialize utility parser with configuration."""
        pass
    
    def parse(self, file_path):
        """
        Parse utility data file.
        
        Args:
            file_path: Path to utility export file
            
        Returns:
            Dict with records, errors, and warnings
        """
        records = []
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_idx, row in enumerate(reader, start=2):
                    try:
                        parsed = self._parse_row(row)
                        if parsed:
                            records.append(parsed)
                            warn = self._check_warnings(parsed)
                            if warn:
                                warnings.append({'row': row_idx, 'warning': warn})
                    except Exception as e:
                        errors.append({
                            'row': row_idx,
                            'error': str(e),
                            'data': row
                        })
        except Exception as e:
            errors.append({'file_error': str(e)})
        
        return {
            'records': records,
            'errors': errors,
            'warnings': warnings,
        }
    
    def _parse_row(self, row):
        """Parse a single utility record."""
        try:
            meter_id = row.get('Meter ID', '').strip()
            location = row.get('Facility Location', '').strip()
            reading_date_str = row.get('Reading Date', '').strip()
            consumption_str = row.get('Consumption (kWh)', '').strip()
            demand_str = row.get('Demand (kW)', '').strip() or None
            tariff_name = row.get('Tariff Name', '').strip() or ''
            rate_str = row.get('Rate ($/kWh)', '').strip() or None
            billing_start_str = row.get('Billing Period Start', '').strip()
            billing_end_str = row.get('Billing Period End', '').strip()
            amount_str = row.get('Amount ($)', '').strip() or None
            
            if not all([meter_id, location, reading_date_str, consumption_str]):
                return None
            
            reading_date = self._parse_date(reading_date_str)
            billing_start = self._parse_date(billing_start_str)
            billing_end = self._parse_date(billing_end_str)
            
            consumption_kwh = Decimal(consumption_str.replace(',', '.'))
            demand_kw = Decimal(demand_str.replace(',', '.')) if demand_str else None
            rate = Decimal(rate_str.replace(',', '.')) if rate_str else None
            amount = Decimal(amount_str.replace(',', '.')) if amount_str else None
            
            return {
                'meter_id': meter_id,
                'facility_location': location,
                'reading_date': reading_date,
                'consumption_kwh_original': consumption_kwh,
                'consumption_kwh': consumption_kwh,
                'demand_kw': demand_kw,
                'billing_period_start': billing_start,
                'billing_period_end': billing_end,
                'tariff_name': tariff_name,
                'rate_per_kwh': rate,
                'amount': amount,
                'currency': 'USD',
            }
        except Exception as e:
            raise ValueError(f"Failed to parse utility row: {str(e)}")
    
    def _parse_date(self, date_str):
        """Parse date from string (handles multiple formats)."""
        if not date_str:
            return None
            
        formats = ['%Y%m%d', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        
        return None
    
    def _check_warnings(self, record):
        """Check for unusual patterns in utility data."""
        consumption = record['consumption_kwh']
        
        if consumption > Decimal('1000000'):
            return 'Extremely high consumption (>1M kWh)'
        
        if consumption < Decimal('1'):
            return 'Unusually low or zero consumption'
        
        if record['demand_kw'] and record['demand_kw'] > Decimal('10000'):
            return 'Unusually high peak demand'
        
        return None
