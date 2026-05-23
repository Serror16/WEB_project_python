from marshmallow import Schema, fields, validate
from dataclasses import dataclass

class RegisterRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))


class RegisterResponseSchema(Schema):
    id = fields.Str(required=True)
    email = fields.Str(required=True)
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    message = fields.Str(required=True)


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class LoginResponseSchema(Schema):
    id = fields.Str(required=True)
    email = fields.Str(required=True)
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    message = fields.Str(required=True)


class RefreshToAccessRequestSchema(Schema):
    refresh = fields.Str(required=True)


class RefreshToAccessResponseSchema(Schema):
    access = fields.Str(required=True)


class LogoutRequestSchema(Schema):
    refresh = fields.Str(required=True)


class LogoutResponseSchema(Schema):
    message = fields.Str(required=True)

@dataclass
class LoginRequest:
    email: str
    password: str

@dataclass
class RefreshToAccessRequest:
    refresh: str

@dataclass
class LogoutRequest:
    refresh: str

@dataclass
class RegisterRequest:
    email: str
    password: str
