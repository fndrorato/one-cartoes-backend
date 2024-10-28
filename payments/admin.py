from django.contrib import admin
from .models import Product, TransactionType, Bank, Modality, PaymentStatus, Received, TypeCard, ServicosPagos

# Register your models here.
admin.site.register(Product)
admin.site.register(TransactionType)
admin.site.register(Modality)
admin.site.register(Bank)
admin.site.register(PaymentStatus)
admin.site.register(Received)
admin.site.register(TypeCard)
admin.site.register(ServicosPagos)