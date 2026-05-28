"""
API views for ESG data ingestion.

Provides endpoints for:
- Uploading ESG data files (SAP, utility, travel)
- Processing and validating incoming data
- Querying ingestion status and history
"""

import os
import tempfile
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from .models import (
    ProcurementRecord, UtilityRecord, TravelRecord,
    DataIngestionLog, Organization
)
from .serializers import (
    ProcurementRecordSerializer, UtilityRecordSerializer,
    TravelRecordSerializer, DataIngestionLogSerializer,
    BulkRecordReviewSerializer
)
from .parsers.sap_parser import SAPDataParser
from .parsers.utility_parser import UtilityDataParser
from .parsers.travel_parser import TravelDataParser


def get_default_org():
    """Helper function to get default organization."""
    import uuid
    org_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    try:
        return Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return None


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics."""
    org = get_default_org()
    
    return Response({
        'procurement_pending': ProcurementRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).count(),
        'procurement_approved': ProcurementRecord.objects.filter(
            organization=org, review_status='APPROVED'
        ).count(),
        'utility_pending': UtilityRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).count(),
        'utility_approved': UtilityRecord.objects.filter(
            organization=org, review_status='APPROVED'
        ).count(),
        'travel_pending': TravelRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).count(),
        'travel_approved': TravelRecord.objects.filter(
            organization=org, review_status='APPROVED'
        ).count(),
    })


class ProcurementViewSet(viewsets.ViewSet):
    """ViewSet for SAP procurement data ingestion."""
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload SAP procurement data file."""
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        org = get_default_org()
        if not org:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
        
        try:
            with os.fdopen(temp_fd, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            parser = SAPDataParser()
            result = parser.parse(temp_path)
            
            ingestion = DataIngestionLog.objects.create(
                organization=org,
                source_type='SAP_PROCUREMENT',
                filename=file.name,
                row_count=len(result['records']),
                error_count=len(result['errors']),
                status='COMPLETED' if not result['errors'] else 'COMPLETED'
            )
            
            for record_data in result['records']:
                record_data['organization'] = org
                record_data['ingestion'] = ingestion
                ProcurementRecord.objects.create(**record_data)
            
            return Response({
                'status': 'success',
                'ingestion_id': str(ingestion.id),
                'rows_ingested': len(result['records']),
                'errors': result['errors']
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending procurement records."""
        org = get_default_org()
        records = ProcurementRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).order_by('-created_at')
        serializer = ProcurementRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all procurement records."""
        org = get_default_org()
        records = ProcurementRecord.objects.filter(
            organization=org
        ).order_by('-created_at')
        serializer = ProcurementRecordSerializer(records, many=True)
        return Response(serializer.data)


class UtilityViewSet(viewsets.ViewSet):
    """ViewSet for utility/energy consumption data ingestion."""
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload utility data file."""
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        org = get_default_org()
        if not org:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
        
        try:
            with os.fdopen(temp_fd, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            parser = UtilityDataParser()
            result = parser.parse(temp_path)
            
            ingestion = DataIngestionLog.objects.create(
                organization=org,
                source_type='UTILITY_ELECTRICITY',
                filename=file.name,
                row_count=len(result['records']),
                error_count=len(result['errors']),
                warnings_count=len(result['warnings']),
                status='COMPLETED'
            )
            
            for record_data in result['records']:
                record_data['organization'] = org
                record_data['ingestion'] = ingestion
                UtilityRecord.objects.create(**record_data)
            
            return Response({
                'status': 'success',
                'ingestion_id': str(ingestion.id),
                'rows_ingested': len(result['records']),
                'warnings': result['warnings'],
                'errors': result['errors']
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending utility records."""
        org = get_default_org()
        records = UtilityRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).order_by('-created_at')
        serializer = UtilityRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all utility records."""
        org = get_default_org()
        records = UtilityRecord.objects.filter(
            organization=org
        ).order_by('-created_at')
        serializer = UtilityRecordSerializer(records, many=True)
        return Response(serializer.data)


class TravelViewSet(viewsets.ViewSet):
    """ViewSet for business travel data ingestion."""
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload travel data file."""
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        org = get_default_org()
        if not org:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
        
        try:
            with os.fdopen(temp_fd, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            parser = TravelDataParser()
            result = parser.parse(temp_path)
            
            ingestion = DataIngestionLog.objects.create(
                organization=org,
                source_type='TRAVEL_CORPORATE',
                filename=file.name,
                row_count=len(result['records']),
                error_count=len(result['errors']),
                warnings_count=len(result['warnings']),
                status='COMPLETED'
            )
            
            for record_data in result['records']:
                record_data['organization'] = org
                record_data['ingestion'] = ingestion
                TravelRecord.objects.create(**record_data)
            
            return Response({
                'status': 'success',
                'ingestion_id': str(ingestion.id),
                'rows_ingested': len(result['records']),
                'warnings': result['warnings'],
                'errors': result['errors']
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending travel records."""
        org = get_default_org()
        records = TravelRecord.objects.filter(
            organization=org, review_status='PENDING'
        ).order_by('-created_at')
        serializer = TravelRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all travel records."""
        org = get_default_org()
        records = TravelRecord.objects.filter(
            organization=org
        ).order_by('-created_at')
        serializer = TravelRecordSerializer(records, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def review_procurement(request):
    """Bulk review procurement records."""
    org = get_default_org()
    serializer = BulkRecordReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        record_ids = serializer.validated_data['record_ids']
        status_val = serializer.validated_data['review_status']
        comments = serializer.validated_data.get('comments', '')
        reviewed_by = serializer.validated_data.get('reviewed_by', 'Analyst')
        
        updated = ProcurementRecord.objects.filter(
            organization=org,
            id__in=record_ids
        ).update(
            review_status=status_val,
            review_comments=comments,
            reviewed_by=reviewed_by,
            reviewed_at=timezone.now()
        )
        
        return Response({'updated_count': updated})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def review_utility(request):
    """Bulk review utility records."""
    org = get_default_org()
    serializer = BulkRecordReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        record_ids = serializer.validated_data['record_ids']
        status_val = serializer.validated_data['review_status']
        comments = serializer.validated_data.get('comments', '')
        reviewed_by = serializer.validated_data.get('reviewed_by', 'Analyst')
        
        updated = UtilityRecord.objects.filter(
            organization=org,
            id__in=record_ids
        ).update(
            review_status=status_val,
            review_comments=comments,
            reviewed_by=reviewed_by,
            reviewed_at=timezone.now()
        )
        
        return Response({'updated_count': updated})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def review_travel(request):
    """Bulk review travel records."""
    org = get_default_org()
    serializer = BulkRecordReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        record_ids = serializer.validated_data['record_ids']
        status_val = serializer.validated_data['review_status']
        comments = serializer.validated_data.get('comments', '')
        reviewed_by = serializer.validated_data.get('reviewed_by', 'Analyst')
        
        updated = TravelRecord.objects.filter(
            organization=org,
            id__in=record_ids
        ).update(
            review_status=status_val,
            review_comments=comments,
            reviewed_by=reviewed_by,
            reviewed_at=timezone.now()
        )
        
        return Response({'updated_count': updated})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
