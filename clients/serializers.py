from rest_framework import serializers
from .models import Groups, Clients

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = ['id', 'name', 'token', 'is_active', 'created_at', 'updated_at', 'created_by', 'notes']
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        # Automaticamente define o `created_by` como o usuário autenticado
        request = self.context['request']
        validated_data['created_by'] = request.user
        return super().create(validated_data)
    
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = '__all__'  # Isso incluirá todos os campos do modelo 
        read_only_fields = ['created_at', 'updated_at', 'created_by']   
        
    def create(self, validated_data):
        # Automaticamente define o `created_by` como o usuário autenticado
        request = self.context['request']
        validated_data['created_by'] = request.user
        return super().create(validated_data)        
