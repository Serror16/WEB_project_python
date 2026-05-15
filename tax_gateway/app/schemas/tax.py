from pydantic import BaseModel, Field, UUID4, model_validator
from decimal import Decimal
from typing import Dict, Any


class TaxReportRequest(BaseModel):
    # здесь country опционален на уровне тела,
    # но ниже в роутере должен передаваться в юрл
    country: str = Field(..., min_length=2, max_length=30)
    idempotency_key: UUID4
    taxpayer_id: str = Field(..., max_length=50)
    amount: Decimal = Field(..., max_digits=12, decimal_places=2)
    currency: str = Field(..., min_length=3, max_length=3)
    year: int = Field(..., ge=2000, le=2100)

    # тут будут лежать все остальные поля
    payload: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def pack_extra_fields_to_payload(cls, data: Any) -> Any:
        # скип, если данные не в виде словаря
        if not isinstance(data, dict):
            return data

        known_fields = {'country', 'idempotency_key', 'taxpayer_id', 'amount', 'currency', 'year', 'payload'}

        # разделение на важные и нет поля
        clean_data = {k: v for k, v in data.items() if k in known_fields}
        extra_data = {k: v for k, v in data.items() if k not in known_fields}

        # обработка payload
        existing_payload = data.get('payload', {})
        if isinstance(existing_payload, dict):
            clean_data['payload'] = {**existing_payload, **extra_data}
        else:
            clean_data['payload'] = extra_data

        return clean_data


# модель для ответа
class TaxReportResponse(BaseModel):
    status: str
    report_id: str
    adapter_details: Dict[str, Any] = {}