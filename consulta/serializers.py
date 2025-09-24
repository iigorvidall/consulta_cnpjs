from rest_framework import serializers


class CNPJQuerySerializer(serializers.Serializer):
    cnpj = serializers.CharField()

    def validate_cnpj(self, value: str) -> str:
        digits = ''.join(ch for ch in value if ch.isdigit())
        if len(digits) != 14:
            raise serializers.ValidationError('CNPJ inválido. Deve conter 14 dígitos.')
        return digits
