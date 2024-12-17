from django.urls import path
from .views import (
    dashboard_view, 
    ReceivedDataView, 
    ExportDashboardView, 
    SharedLinkCreateView, 
    ComparativeDataView,
    SharedLinkDashboardView,
    ExportDashboardView)

urlpatterns = [
    path('dashboard/analytics', ReceivedDataView.as_view(), name='dashboard'),
    path('dashboard/comparative', ComparativeDataView.as_view(), name='dashboard-comparative'),
    # path('dashboard/create-shared-link', SharedLinkCreateView.as_view(), name='create-shared-link'),
    path('dashboard/shared', SharedLinkDashboardView.as_view(), name='shared-link-dashboard'),
    path('dashboard/export-data-dashboard', ExportDashboardView.as_view(), name='dashboard-export-data'),
]
