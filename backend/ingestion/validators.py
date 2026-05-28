"""
Data validators for ESG ingestion.

Contains validation logic for incoming ESG data from various sources.
Ensures data quality and compliance with defined schemas before processing.
"""


def validate_sap_procurement_data(data):
    """
    Validate SAP procurement data structure and content.
    
    Args:
        data: Raw procurement data to validate
        
    Raises:
        ValidationError: If data doesn't meet requirements
    """
    pass


def validate_utility_data(data):
    """
    Validate utility/energy consumption data.
    
    Args:
        data: Raw utility consumption data
        
    Raises:
        ValidationError: If data is invalid
    """
    pass


def validate_travel_data(data):
    """
    Validate travel expense and mileage data.
    
    Args:
        data: Raw travel data
        
    Raises:
        ValidationError: If data format is incorrect
    """
    pass
