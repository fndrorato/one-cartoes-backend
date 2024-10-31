from rest_framework import serializers
from .models import SharedLink

class SharedLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedLink
        fields = [
            'code_url', 
            'client', 
            'info', 
            'date_start', 
            'date_end', 
            'info_action_01', 
            'action_01', 
            'info_action_02', 
            'action_02', 
            'info_action_03', 
            'action_03', 
            'info_action_04', 
            'action_04',
            'download_url'
        ]

        read_only_fields = ['code_url']  # Não permita que o usuário defina o code_url


class ModalityResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    venda = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    taxa = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
