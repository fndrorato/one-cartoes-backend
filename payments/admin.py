from django.contrib import admin
from .models import Product, TransactionType, Bank, Modality, PaymentStatus, Received, TypeCard, ServicosPagos, ReceivedUpdateLog

# Register your models here.
admin.site.register(TransactionType)
admin.site.register(Modality)
admin.site.register(Bank)
admin.site.register(PaymentStatus)
admin.site.register(Received)
admin.site.register(TypeCard)
admin.site.register(ServicosPagos)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista do admin
    list_display = ('code', 'name', 'product_id', 'type_card', 'is_main', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_main', 'is_active', 'type_card')  # Filtros laterais
    search_fields = ('name', 'code')  # Campos que permitem busca
    ordering = ('-created_at',)  # Ordenação padrão por data de criação decrescente
    readonly_fields = ('created_at', 'updated_at')  # Campos somente leitura

    # Exibir o campo `type_card` apenas se ele estiver associado a um cartão
    def type_card(self, obj):
        return obj.type_card.name if obj.type_card else '-'
    type_card.short_description = 'Tipo de Cartão'
    
@admin.register(ReceivedUpdateLog)
class ReceivedUpdateLogAdmin(admin.ModelAdmin):
    list_display = ('received', 'updated_at', 'updated_by')
    list_filter = ('updated_at', 'updated_by')
    search_fields = ('received__id',)    