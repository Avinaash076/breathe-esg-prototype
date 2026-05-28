"""
Travel expense and mileage data parser.

Parses business travel records and expense reports,
converts data to carbon footprint calculations.
"""

import csv
from datetime import datetime
from decimal import Decimal


class TravelDataParser:
    """Parser for corporate travel data."""
    
    AIRPORT_DISTANCES = {
        ('SFO', 'NYC'): 4130,
        ('NYC', 'SFO'): 4130,
        ('LAX', 'LAS'): 270,
        ('LAS', 'LAX'): 270,
        ('ORD', 'MIA'): 2000,
        ('MIA', 'ORD'): 2000,
        ('SEA', 'SFO'): 1300,
        ('SFO', 'SEA'): 1300,
    }
    
    def __init__(self):
        """Initialize travel data parser."""
        pass
    
    def parse(self, file_path):
        """
        Parse travel data file.
        
        Args:
            file_path: Path to travel export file
            
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
        """Parse a single travel record."""
        try:
            trip_id = row.get('Trip ID', '').strip()
            traveler = row.get('Traveler Name', '').strip()
            travel_date_str = row.get('Travel Date', '').strip()
            travel_type = row.get('Travel Type', '').strip().upper()
            origin = row.get('Origin', '').strip()
            destination = row.get('Destination', '').strip()
            distance_str = row.get('Distance (km)', '').strip() or None
            cost_str = row.get('Cost ($)', '').strip() or None
            currency = row.get('Currency', 'USD').strip()
            notes = row.get('Notes', '').strip() or ''
            
            if not all([trip_id, traveler, travel_date_str, travel_type, cost_str]):
                return None
            
            travel_date = self._parse_date(travel_date_str)
            
            if travel_type not in ['FLIGHT', 'HOTEL', 'GROUND_TRANSPORT']:
                travel_type = 'FLIGHT' if travel_type in ['AIR', 'FLIGHTS'] else \
                              'HOTEL' if travel_type in ['ACCOMMODATION', 'LODGING'] else \
                              'GROUND_TRANSPORT' if travel_type in ['GROUND', 'TAXI', 'RENTAL'] else \
                              'FLIGHT'
            
            cost = Decimal(cost_str.replace(',', '.').replace('$', ''))
            distance_km = Decimal(distance_str.replace(',', '.')) if distance_str else None
            
            if not distance_km and travel_type == 'FLIGHT':
                distance_km = self._infer_distance(origin, destination)
            elif travel_type == 'HOTEL':
                distance_km = Decimal('0')
            elif not distance_km and travel_type == 'GROUND_TRANSPORT':
                distance_km = Decimal('50')
            
            return {
                'trip_id': trip_id,
                'traveler_name': traveler,
                'travel_date': travel_date,
                'travel_type': travel_type,
                'origin': origin,
                'destination': destination,
                'distance_km': distance_km,
                'amount': cost,
                'currency': currency,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse travel row: {str(e)}")
    
    def _parse_date(self, date_str):
        """Parse date from string (handles multiple formats)."""
        if not date_str:
            return None
        
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        
        return None
    
    def _infer_distance(self, origin, destination):
        """Infer distance from airport codes."""
        origin_code = origin.upper()
        dest_code = destination.upper()
        
        if (origin_code, dest_code) in self.AIRPORT_DISTANCES:
            return Decimal(str(self.AIRPORT_DISTANCES[(origin_code, dest_code)]))
        
        return Decimal('2000')
    
    def _check_warnings(self, record):
        """Check for unusual patterns in travel data."""
        distance = record['distance_km']
        cost = record['amount']
        travel_type = record['travel_type']
        
        if travel_type == 'FLIGHT' and distance < Decimal('300'):
            return 'Short flight (<300km) - should consider ground transport'
        
        if cost > Decimal('10000'):
            return 'Unusually high cost (>$10k)'
        
        if travel_type == 'HOTEL' and distance and distance > Decimal('0'):
            return 'Hotel record has distance assigned (data error?)'
        
        return None
