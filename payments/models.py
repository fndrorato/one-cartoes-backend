from django.db import models
from adquirentes.models import Acquirer
from clients.models import Clients
from django.contrib.auth import get_user_model

User = get_user_model()

class TypeCard(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'        

class Product(models.Model):
    code = models.IntegerField(default=0) # codigo do produto que vem da API da Conciliadora
    name = models.CharField(max_length=50)
    product_id = models.IntegerField(default=0)
    type_card = models.ForeignKey(TypeCard, on_delete=models.RESTRICT, null=True, blank=True)
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} - ({self.type_card.name})' if self.type_card else self.name
    
class TransactionType(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f'{self.id} - {self.name}'
    
class Modality(models.Model):
    code = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f'{self.code} - {self.name}' 
    
class Bank(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f'{self.id} - {self.name}'
    
class PaymentStatus(models.Model):
    code = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f'{self.code} - {self.description}'   
    
class ServicosPagos(models.Model):
    observacao = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.observacao}'     
    
class Received(models.Model):
    id = models.BigAutoField(primary_key=True) # Identificador do pagamento
    id_pagamento = models.CharField(max_length=100, blank=True, null=True) # Identificador do cliente na venda
    refo_id = models.IntegerField() # Identificador interno da empresa
    client = models.ForeignKey(Clients, on_delete=models.RESTRICT)  # Chave estrangeira para o modelo Clients
    estabelecimento = models.CharField(max_length=50, null=True, blank=True) # Identificador do estabelecimento
    data_pagamento = models.DateField(null=True, blank=True)
    data_prevista_pagamento = models.DateField(null=True, blank=True)
    data_venda = models.DateField(null=True, blank=True)
    adquirente = models.ForeignKey(Acquirer, on_delete=models.RESTRICT)
    autorizacao = models.CharField(max_length=50, null=True, blank=True) # Número da autorização
    nsu = models.CharField(max_length=50, null=True, blank=True) # Número do NSU
    id_transacao = models.CharField(max_length=50, null=True, blank=True) # Identificador único da transação
    parcela = models.IntegerField(default=0) # Número da parcela
    total_parcelas = models.IntegerField(default=0) # Número Total das parcelas
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    resumo_venda = models.CharField(max_length=250, null=True, blank=True)
    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    taxa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Porcentagem da taxa por transação
    outras_despesas = models.DecimalField(max_digits=10, decimal_places=2) # Valor de outras despesas
    valor_liquido = models.DecimalField(max_digits=10, decimal_places=2)
    idt_antecipacao = models.BooleanField(default=False)  # Identificador de antecipação
    banco = models.ForeignKey(Bank, on_delete=models.RESTRICT)
    agencia = models.CharField(max_length=50, null=True, blank=True)
    conta = models.CharField(max_length=50, null=True, blank=True)
    nome_loja = models.CharField(max_length=50, null=True, blank=True) # Descrição da Loja por Terminal
    terminal = models.CharField(max_length=50, null=True, blank=True) # Identificador do terminal de venda
    transactiontype = models.ForeignKey(TransactionType, on_delete=models.RESTRICT)
    id_status = models.ForeignKey(PaymentStatus, on_delete=models.RESTRICT) # identificador do status
    divergencias = models.CharField(max_length=250, null=True, blank=True)
    valor_liquido_venda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observacao  = models.CharField(max_length=250, null=True, blank=True)
    motivo_ajuste  = models.CharField(max_length=250, null=True, blank=True)
    conta_adquirente = models.BooleanField(null=True, blank=True)
    taxa_antecipacao = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    taxa_antecipacao_mensal = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valor_taxa_antecipacao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_taxa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Valor da taxa por transação
    modality = models.ForeignKey(Modality, on_delete=models.RESTRICT)    
    tem_conciliacao_bancaria = models.BooleanField(default=False)
    cartao = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.client.name} - {self.id} - {self.data_pagamento.strftime("%Y-%m-%d") if self.data_pagamento else "Data não disponível"}'
