from django.urls import path
from .views import (
    dashboard_view, 
    ReceivedDataView, 
    ExportDashboardView, 
    SharedLinkCreateView, 
    SharedLinkDashboardView)

urlpatterns = [
    # path('dashboard/analytics', dashboard_view, name='dash-teste'),
    path('dashboard/analytics', ReceivedDataView.as_view(), name='dashboard'),
    path('dashboard/create-shared-link', SharedLinkCreateView.as_view(), name='create-shared-link'),
    path('dashboard/shared', SharedLinkDashboardView.as_view(), name='shared-link-dashboard'),
    path('dashboard/export', ExportDashboardView.as_view(), name='dashboard-export'),
]
