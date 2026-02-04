from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.auth import APIKeyStatus


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    max_api_keys: int = Field(default=5, ge=1, le=50)
    rate_limit_per_minute: int = Field(default=60, ge=1)
    rate_limit_per_day: int = Field(default=10000, ge=1)


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = None
    is_active: Optional[bool] = None
    max_api_keys: Optional[int] = Field(None, ge=1, le=50)
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)
    rate_limit_per_day: Optional[int] = Field(None, ge=1)


class ClientResponse(BaseModel):
    id: int
    name: str
    company: str
    email: str
    is_active: bool
    max_api_keys: int
    rate_limit_per_minute: int
    rate_limit_per_day: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome da API Key")
    description: Optional[str] = Field(None, max_length=1000)
    environment: str = Field("production", description="production ou test")
    permissions: List[str] = Field(..., min_items=1, description="Lista de permissões")
    allowed_ips: Optional[List[str]] = Field(None, description="IPs permitidos (opcional)")
    allowed_domains_ids: Optional[List[int]] = Field(None, description="IDs de domínios permitidos")
    expires_in_days: Optional[int] = Field(None, ge=1, description="Dias até expiração")
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        if v not in ['production', 'test']:
            raise ValueError('environment deve ser "production" ou "test"')
        return v


class APIKeyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    key_preview: str
    full_key: Optional[str] = None  # Apenas no create
    status: APIKeyStatus
    permissions: List[str]
    allowed_ips: Optional[List[str]] = None
    allowed_domains_ids: Optional[List[int]] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    total_requests: int
    expires_at: Optional[datetime] = None
    warning: Optional[str] = None
    
    class Config:
        from_attributes = True


class APIKeyListItem(BaseModel):
    id: int
    name: str
    key_preview: str
    status: APIKeyStatus
    permissions: List[str]
    created_at: datetime
    last_used_at: Optional[datetime] = None
    total_requests: int
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UsageLogResponse(BaseModel):
    id: int
    endpoint: str
    method: str
    status_code: Optional[int] = None
    ip_address: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientInfoResponse(BaseModel):
    client: ClientResponse
    api_key_info: dict
    usage_summary: dict
