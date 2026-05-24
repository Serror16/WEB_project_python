


from marshmallow import Schema, fields


class ErrorResponse(Schema):
    """Единый формат ошибок (по ТЗ)"""
    error_code = fields.Str(required=True)
    message = fields.Str(required=True)
    details = fields.Dict(required=False, dump_default={})