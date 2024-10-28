from django.urls import path
from .views import ReceivedListView

urlpatterns = [
    path('report/payments', ReceivedListView.as_view(), name='list-payments'),
]
