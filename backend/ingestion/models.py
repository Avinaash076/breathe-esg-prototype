"""
Models for ESG data ingestion and storage.

Defines Django ORM models for persisting ESG data from various sources:
- Procurement data from SAP systems
- Utility consumption records
- Travel and business expense data
"""

from django.db import models
from django.utils import timezone
import uuid


class Organization(models.Model):
    """Multi-tenant organization model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class DataIngestionLog(models.Model):
    """
    Model for tracking data ingestion events and status.
    Records import history, validation results, and processing status.
    Source of truth for which original file produced which records.
    """
    SOURCE_CHOICES = [
        ('SAP_PROCUREMENT', 'SAP Procurement & Fuel'),
        ('UTILITY_ELECTRICITY', 'Utility - Electricity'),
        ('TRAVEL_CORPORATE', 'Corporate Travel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    filename = models.CharField(max_length=255)
    ingestion_timestamp = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    warnings_count = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')],
        default='PENDING'
    )
    error_details = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = 'ingestion'
    
    def __str__(self):
        return f"{self.source_type} - {self.filename} - {self.ingestion_timestamp}"


class SAPPlant(models.Model):
    """Lookup table for SAP plant codes."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    plant_code = models.CharField(max_length=10)
    plant_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    
    class Meta:
        app_label = 'ingestion'
        unique_together = ('organization', 'plant_code')


class Supplier(models.Model):
    """Lookup table for suppliers."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    supplier_code = models.CharField(max_length=20)
    supplier_name = models.CharField(max_length=255)
    
    class Meta:
        app_label = 'ingestion'
        unique_together = ('organization', 'supplier_code')


class ProcurementRecord(models.Model):
    """
    Model for SAP procurement and supplier data.
    Stores supplier information, material types, and procurement amounts.
    Normalized for audit and carbon accounting.
    """
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1'),
        ('SCOPE_2', 'Scope 2'),
        ('SCOPE_3', 'Scope 3'),
    ]
    
    REVIEW_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked for Audit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    ingestion = models.ForeignKey(DataIngestionLog, on_delete=models.SET_NULL, null=True)
    
    # Original data (as received from SAP)
    document_number = models.CharField(max_length=50)
    line_item = models.CharField(max_length=10)
    plant_code = models.CharField(max_length=10)
    material_code = models.CharField(max_length=50)
    vendor_code = models.CharField(max_length=20, blank=True)
    vendor_name = models.CharField(max_length=255)
    
    # Original quantities and units
    quantity_original = models.DecimalField(max_digits=15, decimal_places=4)
    unit_original = models.CharField(max_length=10)  # kg, tonnes, liters, etc.
    
    # Normalized values
    quantity_tonnes = models.DecimalField(max_digits=15, decimal_places=6, null=True)  # Normalized to tonnes
    
    # Procurement details
    procurement_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Carbon accounting
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='SCOPE_3')
    emission_category = models.CharField(max_length=100, blank=True)  # fuel, purchased goods, etc.
    
    # Audit trail
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='PENDING')
    review_comments = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=255, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Flags
    suspicious_flag = models.BooleanField(default=False)  # For anomalies
    suspicious_reason = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ingestion'
        indexes = [
            models.Index(fields=['organization', 'procurement_date']),
            models.Index(fields=['organization', 'review_status']),
        ]


class UtilityRecord(models.Model):
    """
    Model for utility and energy consumption data.
    Tracks electricity, water, and gas usage across facilities.
    Handles multi-month billing periods and tariff complexity.
    """
    SCOPE_CHOICES = [
        ('SCOPE_2', 'Scope 2 - Purchased Electricity'),
    ]
    
    REVIEW_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked for Audit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    ingestion = models.ForeignKey(DataIngestionLog, on_delete=models.SET_NULL, null=True)
    
    # Original data
    meter_id = models.CharField(max_length=50)
    facility_location = models.CharField(max_length=255)
    reading_date = models.DateField()
    
    # Consumption data
    consumption_kwh_original = models.DecimalField(max_digits=15, decimal_places=2)
    consumption_kwh = models.DecimalField(max_digits=15, decimal_places=2)  # Normalized/verified
    
    # Optional demand (peak usage)
    demand_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Billing period info
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    
    # Tariff/rate info
    tariff_name = models.CharField(max_length=100, blank=True)
    rate_per_kwh = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    # Audit trail
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='PENDING')
    review_comments = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=255, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Flags
    suspicious_flag = models.BooleanField(default=False)
    suspicious_reason = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ingestion'
        indexes = [
            models.Index(fields=['organization', 'reading_date']),
            models.Index(fields=['organization', 'review_status']),
        ]


class TravelRecord(models.Model):
    """
    Model for business travel and mileage data.
    Stores employee travel records for carbon accounting.
    Handles flights, hotels, and ground transport.
    """
    TRAVEL_TYPE_CHOICES = [
        ('FLIGHT', 'Flight'),
        ('HOTEL', 'Hotel Night'),
        ('GROUND_TRANSPORT', 'Ground Transport (taxi, car rental, etc)'),
    ]
    
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1 - Corporate Vehicles'),
        ('SCOPE_3', 'Scope 3 - Business Travel'),
    ]
    
    REVIEW_STATUS = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked for Audit'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    ingestion = models.ForeignKey(DataIngestionLog, on_delete=models.SET_NULL, null=True)
    
    # Trip identification
    trip_id = models.CharField(max_length=50)
    traveler_name = models.CharField(max_length=255)
    
    # Travel details
    travel_type = models.CharField(max_length=20, choices=TRAVEL_TYPE_CHOICES)
    travel_date = models.DateField()
    
    # Route
    origin = models.CharField(max_length=100, blank=True)  # City or Airport code
    destination = models.CharField(max_length=100, blank=True)  # City or Airport code
    
    # Distance (km) - for flights calculated from airport codes, for ground from platform
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Cost
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Carbon accounting
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='SCOPE_3')
    
    # Audit trail
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='PENDING')
    review_comments = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=255, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Flags
    suspicious_flag = models.BooleanField(default=False)
    suspicious_reason = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'ingestion'
        indexes = [
            models.Index(fields=['organization', 'travel_date']),
            models.Index(fields=['organization', 'review_status']),
        ]
    class Meta:
        app_label = 'ingestion'
    # Fields to be implemented
    pass
