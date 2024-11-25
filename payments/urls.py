from django.urls import path
from .views import ReceivedListView, UpdateReceivedView

urlpatterns = [
    path('report/payments', ReceivedListView.as_view(), name='list-payments'),
    path('received/<int:pk>/update/', UpdateReceivedView.as_view(), name='update-received'),
]
