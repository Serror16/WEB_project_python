# Унифицированная модель ошибки по ТЗ: {error_code, message, details}.
# Используется для генерации одинаковых ответов при любых сбоях системы.

from marshmallow import Schema, fields


class ErrorResponse(Schema):
    """Единый формат ошибок (по ТЗ)"""
    error_code = fields.Str(required=True)
    message = fields.Str(required=True)
    details = fields.Dict(required=False, missing={})