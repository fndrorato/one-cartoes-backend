from rest_framework import serializers
from .models import Received
from datetime import datetime

class ReceivedSerializer(serializers.ModelSerializer):
    id_received = serializers.IntegerField(source='id', read_only=True) 
    
    id_modalidade = serializers.IntegerField(source='modality.id', read_only=True) 
    nome_modalidade = serializers.CharField(source='modality.name', read_only=True)
    id_produto = serializers.IntegerField(source='product.id', read_only=True)  
    nome_produto = serializers.CharField(source='product.name', read_only=True)  
    id_adquirente = serializers.IntegerField(source='adquirente.id', read_only=True)
    nome_adquirente = serializers.CharField(source='adquirente.name', read_only=True)
    id_tipo_transacao = serializers.IntegerField(source='transactiontype.id', read_only=True)
    nome_tipo_transacao = serializers.CharField(source='transactiontype.name', read_only=True)
    id_status_pagamento = serializers.IntegerField(source='paymentstatus.id', read_only=True)
    descricao_status_pagamento = serializers.CharField(source='paymentstatus.description', read_only=True)
    
    class Meta:
        model = Received
        fields = [
            'id_received',
            'id_pagamento',
            'refo_id',
            'estabelecimento',
            'data_pagamento',
            'data_prevista_pagamento',
            'data_venda',
            'autorizacao',
            'nsu',
            'id_transacao',
            'parcela',
            'total_parcelas',
            'resumo_venda',
            'valor_bruto',
            'taxa',
            'outras_despesas',
            'valor_liquido',
            'idt_antecipacao',
            'agencia',
            'conta',
            'nome_loja',
            'terminal',
            'divergencias',
            'valor_liquido_venda',
            'observacao',
            'motivo_ajuste',
            'conta_adquirente',
            'taxa_antecipacao',
            'taxa_antecipacao_mensal',
            'valor_taxa_antecipacao',
            'valor_taxa',
            'tem_conciliacao_bancaria',
            'cartao',
            'client',
            'id_adquirente',
            'nome_adquirente',
            'id_produto',
            'nome_produto',
            'banco',
            'id_tipo_transacao',
            'nome_tipo_transacao',
            'id_status_pagamento',
            'descricao_status_pagamento',
            'id_modalidade',  
            'nome_modalidade' 
        ]

    # def to_representation(self, instance):
    #     # Obtendo a representação padrão do objeto
    #     representation = super().to_representation(instance)

    #     # Formatação de datas
    #     for date_field in ['data_pagamento', 'data_prevista_pagamento', 'data_venda']:
    #         if representation[date_field]:
    #             representation[date_field] = datetime.strptime(representation[date_field], '%Y-%m-%d').strftime('%d/%m/%Y')

    #     # Formatação de valores
    #     for value_field in ['valor_bruto', 'taxa', 'outras_despesas', 'valor_liquido', 'valor_taxa', 'valor_taxa_antecipacao']:
    #         if representation[value_field]:
    #             representation[value_field] = representation[value_field].replace('.', ',')

    #     return representation        
        
        