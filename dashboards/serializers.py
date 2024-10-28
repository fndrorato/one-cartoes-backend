from rest_framework import serializers
from .models import SharedLink

class SharedLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedLink
        fields = ['code_url', 'client', 'info', 'date_start', 'date_end']
        read_only_fields = ['code_url']  # Não permita que o usuário defina o code_url


class ModalityResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
