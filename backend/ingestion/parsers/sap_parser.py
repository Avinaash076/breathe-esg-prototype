"""
SAP data parser for procurement and supplier data.

Parses procurement records from SAP ERP systems,
handles different export formats and data structures.
"""

import csv
from datetime import datetime
from decimal import Decimal


class SAPDataParser:
    """
    Parser for SAP ERP procurement data.
    Converts SAP exports (CSV, XLSX) into standardized format.
    Handles unit conversions and data normalization.
    """
    
    # Unit conversion factors to tonnes
    UNIT_CONVERSIONS = {
        'KG': Decimal('0.001'),      # kg to tonnes
        'kg': Decimal('0.001'),
        'MT': Decimal('1'),           # metric tonne
        'mt': Decimal('1'),
        'T': Decimal('1'),            # tonne
        't': Decimal('1'),
        'L': Decimal('0'),            # liters - requires density, handle separately
        'l': Decimal('0'),
        'EA': Decimal('0'),           # each - unknown weight
        'PC': Decimal('0'),           # piece - unknown weight
        'CY': Decimal('0'),           # cylinder - unknown weight
        'SHIPMENT': Decimal('0'),     # shipment - unknown weight
    }
    
    # Fuel/Oil density conversions (density in tonnes/litre)
    FUEL_DENSITY = {
        'DIESEL': Decimal('0.832'),
        'GASOLINE': Decimal('0.755'),
        'HFO': Decimal('0.960'),      # Heavy Fuel Oil
        'LPG': Decimal('0.540'),
        'NATURAL_GAS': Decimal('0'),  # Gas - handled separately
    }
    
    # Category detection
    FUEL_KEYWORDS = ['fuel', 'diesel', 'gasoline', 'petrol', 'oil', 'gas', 'lpg', 'hfo']
    PROCUREMENT_KEYWORDS = ['material', 'goods', 'purchase', 'resin', 'steel', 'metal', 'plastic']
    
    def __init__(self):
        """Initialize SAP parser with configuration."""
        self.suspicious_records = []
    
    def parse(self, file_path):
        """
        Parse SAP data file.
        
        Args:
            file_path: Path to SAP export file
            
        Returns:
            List of parsed procurement records dict
        """
        records = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_idx, row in enumerate(reader, start=2):
                    try:
                        parsed = self._parse_row(row)
                        if parsed:
                            records.append(parsed)
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
            'suspicious_count': len(self.suspicious_records)
        }
    
    def _parse_row(self, row):
        """Parse a single SAP row."""
        # Expected columns from SAP export
        try:
            doc_num = row.get('EBELN', '').strip()
            line_item = row.get('', '')  # line item implicit
            plant = row.get('WERKS', '').strip()
            vendor_code = row.get('LIFNR', '').strip()
            vendor_name = row.get('NAME1', '').strip()
            material_code = row.get('MATNR', '').strip()
            description = row.get('TXZ01', '').strip()
            quantity_str = row.get('MENGE', '').strip()
            unit = row.get('MEINS', '').strip()
            amount_str = row.get('NETWR', '').strip()
            currency = row.get('WAERS', 'EUR').strip()
            date_str = row.get('BEDAT', '').strip()
            
            if not all([doc_num, plant, vendor_name, quantity_str, unit, amount_str, date_str]):
                return None
            
            # Parse date (SAP format YYYYMMDD or similar)
            try:
                if len(date_str) == 8:
                    procurement_date = datetime.strptime(date_str, '%Y%m%d').date()
                else:
                    procurement_date = datetime.strptime(date_str, '%d.%m.%Y').date()
            except:
                procurement_date = datetime.now().date()
            
            # Parse numeric values
            quantity = Decimal(quantity_str.replace(',', '.'))
            amount = Decimal(amount_str.replace(',', '.'))
            
            # Normalize quantity to tonnes
            quantity_tonnes = self._convert_to_tonnes(quantity, unit, description)
            
            # Detect category
            emission_category = self._detect_category(description)
            
            # Flag suspicious records
            suspicious, reason = self._check_suspicious(quantity, unit, amount)
            
            return {
                'document_number': doc_num,
                'line_item': line_item or '1',
                'plant_code': plant,
                'material_code': material_code,
                'vendor_code': vendor_code,
                'vendor_name': vendor_name,
                'quantity_original': quantity,
                'unit_original': unit,
                'quantity_tonnes': quantity_tonnes,
                'procurement_date': procurement_date,
                'amount': amount,
                'currency': currency,
                'emission_category': emission_category,
                'scope': 'SCOPE_3',
                'suspicious_flag': suspicious,
                'suspicious_reason': reason,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse row: {str(e)}")
    
    def _convert_to_tonnes(self, quantity, unit, description):
        """Convert quantity to tonnes if possible."""
        unit_upper = unit.upper()
        
        if unit_upper in ['KG', 'MT', 'T']:
            return quantity * self.UNIT_CONVERSIONS[unit_upper]
        
        # For liters (fuel), try to detect fuel type and apply density
        if unit_upper == 'L':
            desc_upper = description.upper()
            for fuel_type, density in self.FUEL_DENSITY.items():
                if fuel_type in desc_upper and density > 0:
                    return quantity * density / Decimal('1000')
        
        # Cannot convert - return None
        return None
    
    def _detect_category(self, description):
        """Detect emission category from description."""
        desc_lower = description.lower()
        
        for keyword in self.FUEL_KEYWORDS:
            if keyword in desc_lower:
                return 'fuel'
        
        for keyword in self.PROCUREMENT_KEYWORDS:
            if keyword in desc_lower:
                return 'purchased_goods'
        
        return 'materials'
    
    def _check_suspicious(self, quantity, unit, amount):
        """Check for suspicious patterns."""
        suspicious = False
        reason = ''
        
        # Suspiciously high amounts for unknown units
        if unit.upper() in ['EA', 'PC', 'SHIPMENT', 'CY']:
            if amount > Decimal('50000'):
                suspicious = True
                reason = f'Very high cost ({amount}) for unit type {unit}'
        
        # Suspiciously low/high quantities
        if quantity < Decimal('0.01'):
            suspicious = True
            reason = 'Extremely small quantity'
        elif quantity > Decimal('1000000'):
            suspicious = True
            reason = 'Extremely large quantity'
        
        return suspicious, reason
    
    
    def validate_record(self, record):
        """
        Validate individual SAP record structure.
        
        Args:
            record: Dictionary of record data
            
        Returns:
            Boolean indicating if record is valid
        """
        pass
    
    def map_fields(self, raw_record):
        """
        Map SAP field names to standardized schema.
        
        Args:
            raw_record: Raw record from SAP export
            
        Returns:
            Record with mapped field names
        """
        pass
