"""
URL routing for ESG ingestion app.

Maps API endpoints for data ingestion, upload processing,
and ingestion status management.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ingestion'

router = DefaultRouter()
router.register(r'procurement', views.ProcurementViewSet, basename='procurement')
router.register(r'utility', views.UtilityViewSet, basename='utility')
router.register(r'travel', views.TravelViewSet, basename='travel')

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard_stats'),
    path('procurement/review/', views.review_procurement, name='review_procurement'),
    path('utility/review/', views.review_utility, name='review_utility'),
    path('travel/review/', views.review_travel, name='review_travel'),
] + router.urls
