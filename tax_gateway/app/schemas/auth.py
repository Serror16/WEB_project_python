from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8)

class RegisterResponse(BaseModel):
    id: str
    email: str
    access_token: str
    refresh_token: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    id: str
    email: str
    access_token: str
    refresh_token: str

class RefreshToAccessRequest(BaseModel):
    refresh: str

class RefreshToAccessResponse(BaseModel):
    access: str

class LogoutRequest(BaseModel):
    refresh: str

class LogoutResponse(BaseModel):
    message: str

