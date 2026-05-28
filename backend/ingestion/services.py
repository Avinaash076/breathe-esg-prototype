"""
Business logic services for ESG data ingestion.

Contains core service classes for processing, transforming,
and storing ESG data from various sources.
"""


class SAPIngestionService:
    """
    Service for processing SAP procurement data.
    Handles extraction, transformation, and loading of SAP records.
    """
    
    def process_sap_file(self, file_path):
        """Process SAP procurement CSV file."""
        pass
    
    def transform_sap_data(self, raw_data):
        """Transform raw SAP data to internal format."""
        pass
    
    def store_sap_records(self, transformed_data):
        """Store processed SAP records in database."""
        pass


class UtilityIngestionService:
    """
    Service for processing utility/energy consumption data.
    Manages electricity, water, and gas usage records.
    """
    
    def process_utility_file(self, file_path):
        """Process utility consumption CSV file."""
        pass
    
    def transform_utility_data(self, raw_data):
        """Transform raw utility data to standardized format."""
        pass
    
    def store_utility_records(self, transformed_data):
        """Store utility records with timestamps and locations."""
        pass


class TravelIngestionService:
    """
    Service for processing travel expense data.
    Converts travel records to carbon footprint metrics.
    """
    
    def process_travel_file(self, file_path):
        """Process travel expense CSV file."""
        pass
    
    def transform_travel_data(self, raw_data):
        """Transform travel data to standardized format."""
        pass
    
    def store_travel_records(self, transformed_data):
        """Store travel records with carbon calculations."""
        pass
