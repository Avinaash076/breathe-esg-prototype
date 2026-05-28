"""
Serializers for ESG ingestion data.

This module contains DRF serializers for converting ESG data models
to/from JSON and performing data validation during API operations.
"""

from rest_framework import serializers
from .models import (
    ProcurementRecord, UtilityRecord, TravelRecord,
    DataIngestionLog, Organization
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'created_at']


class DataIngestionLogSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = DataIngestionLog
        fields = [
            'id', 'organization', 'organization_name', 'source_type',
            'filename', 'ingestion_timestamp', 'row_count',
            'error_count', 'warnings_count', 'status', 'error_details'
        ]
        read_only_fields = ['id', 'ingestion_timestamp']


class ProcurementRecordSerializer(serializers.ModelSerializer):
    ingestion_filename = serializers.CharField(source='ingestion.filename', read_only=True)
    
    class Meta:
        model = ProcurementRecord
        fields = [
            'id', 'organization', 'ingestion', 'ingestion_filename',
            'document_number', 'line_item', 'plant_code', 'material_code',
            'vendor_code', 'vendor_name',
            'quantity_original', 'unit_original', 'quantity_tonnes',
            'procurement_date', 'amount', 'currency',
            'scope', 'emission_category',
            'review_status', 'review_comments', 'reviewed_by', 'reviewed_at',
            'suspicious_flag', 'suspicious_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class UtilityRecordSerializer(serializers.ModelSerializer):
    ingestion_filename = serializers.CharField(source='ingestion.filename', read_only=True)
    
    class Meta:
        model = UtilityRecord
        fields = [
            'id', 'organization', 'ingestion', 'ingestion_filename',
            'meter_id', 'facility_location', 'reading_date',
            'consumption_kwh_original', 'consumption_kwh', 'demand_kw',
            'billing_period_start', 'billing_period_end',
            'tariff_name', 'rate_per_kwh', 'amount', 'currency',
            'review_status', 'review_comments', 'reviewed_by', 'reviewed_at',
            'suspicious_flag', 'suspicious_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class TravelRecordSerializer(serializers.ModelSerializer):
    ingestion_filename = serializers.CharField(source='ingestion.filename', read_only=True)
    
    class Meta:
        model = TravelRecord
        fields = [
            'id', 'organization', 'ingestion', 'ingestion_filename',
            'trip_id', 'traveler_name', 'travel_type', 'travel_date',
            'origin', 'destination', 'distance_km',
            'amount', 'currency', 'scope',
            'review_status', 'review_comments', 'reviewed_by', 'reviewed_at',
            'suspicious_flag', 'suspicious_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class BulkRecordReviewSerializer(serializers.Serializer):
    """Serializer for bulk review/approval operations."""
    record_ids = serializers.ListField(child=serializers.CharField())
    review_status = serializers.ChoiceField(choices=['APPROVED', 'REJECTED', 'LOCKED'])
    comments = serializers.CharField(required=False, allow_blank=True)
    reviewed_by = serializers.CharField(required=False)
