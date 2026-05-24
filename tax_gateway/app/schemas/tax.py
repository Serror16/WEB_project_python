from marshmallow import Schema, fields, validate
from dataclasses import dataclass, field
import uuid
from decimal import Decimal


class TaxReportRequestSchema(Schema):
    idempotency_key = fields.Str(required=True, validate=validate.Regexp(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        error="Неверный формат UUID"
    ))
    taxpayer_id = fields.Str(required=True, validate=validate.Length(max=50))
    amount = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01))
    currency = fields.Str(required=True, validate=validate.Length(min=3, max=3))
    year = fields.Int(required=True, validate=validate.Range(min=2000, max=2100))

    payload = fields.Dict(required=False, load_default={})



class TaxReportResponseSchema(Schema):
    status = fields.Str(required=True)
    report_id = fields.Str(required=True)
    adapter_details = fields.Dict(required=False, dump_default={})

class TaxStatusResponseSchema(Schema):
    report_id = fields.Str(required=True)
    status = fields.Str(required=True)
    message = fields.Str(required=False, allow_none=True)
    processed_at = fields.DateTime(required=False, allow_none=True)

@dataclass
class TaxReportRequest:
    taxpayer_id: str
    amount: Decimal
    currency: str
    year: int
    idempotency_key: uuid.UUID
    country: str
    user_id: str
    payload: dict = field(default_factory=dict)