from rest_framework import serializers

class TaxReportSerializer(serializers.Serializer):
    # обязательные поля
    country = serializers.CharField(required=True)
    idempotency_key = serializers.UUIDField(required=True)
    taxpayer_id = serializers.CharField(max_length=50, required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, required=True)
    year = serializers.IntegerField(min_value=2000, max_value=2100, required=True)

    # все остальное пихается сюда, по типу инн-бик-другой информации...
    payload = serializers.DictField(required=False, default=dict)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            return super().to_internal_value(data)

        known_fields = {
            'country', 'idempotency_key', 'taxpayer_id',
            'amount', 'currency', 'year', 'payload'
        }

        # разделение данных
        clean_data = {k: v for k, v in data.items() if k in known_fields}
        extra_data = {k: v for k, v in data.items() if k not in known_fields}

        # уже есть поле payload или нет?
        existing_payload = data.get('payload', {})
        if isinstance(existing_payload, dict):
            clean_data['payload'] = {**existing_payload, **extra_data}
        else:
            clean_data['payload'] = extra_data

        return super().to_internal_value(clean_data)