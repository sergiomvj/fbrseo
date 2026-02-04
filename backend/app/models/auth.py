from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
import hashlib
import enum
from app.database import Base


class APIKeyStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKeyPermission(str, enum.Enum):
    # Leitura
    READ_KEYWORDS = "keywords:read"
    READ_RANKINGS = "rankings:read"
    READ_BACKLINKS = "backlinks:read"
    READ_ONPAGE = "onpage:read"
    READ_COMPETITORS = "competitors:read"
    READ_REPORTS = "reports:read"
    
    # Escrita
    WRITE_KEYWORDS = "keywords:write"
    WRITE_RANKINGS = "rankings:write"
    IMPORT_DATA = "data:import"
    
    # Admin
    ADMIN_FULL = "admin:*"


class Client(Base):
    """
    Representa uma empresa, departamento ou sistema consumidor
    """
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Configurações
    is_active = Column(Boolean, default=True)
    max_api_keys = Column(Integer, default=5)
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    api_keys = relationship("APIKey", back_populates="client", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="client")
    usage_logs = relationship("UsageLog", back_populates="client")


class APIKey(Base):
    """
    API Keys para autenticação
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    
    # Key
    key_prefix = Column(String(20), nullable=False)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    key_last_chars = Column(String(8), nullable=False)
    
    # Metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Status e Permissões
    status = Column(Enum(APIKeyStatus), default=APIKeyStatus.ACTIVE, nullable=False)
    permissions = Column(JSON, nullable=False)
    
    # Restrições
    allowed_ips = Column(JSON)
    allowed_domains_ids = Column(JSON)
    
    # Expiração
    expires_at = Column(DateTime, nullable=True)
    
    # Uso
    last_used_at = Column(DateTime)
    total_requests = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    client = relationship("Client", back_populates="api_keys")
    
    @staticmethod
    def generate_key(prefix: str = "sk_live") -> tuple:
        """
        Gera uma nova API key
        Returns: (full_key, key_hash, last_4_chars)
        """
        random_part = secrets.token_urlsafe(32)
        full_key = f"{prefix}_{random_part}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        last_chars = full_key[-4:]
        
        return full_key, key_hash, last_chars
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash de uma API key"""
        return hashlib.sha256(key.encode()).hexdigest()


class UsageLog(Base):
    """
    Log de uso das API Keys
    """
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True)
    
    # Request info
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    
    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(Text)
    response_time_ms = Column(Integer)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relacionamentos
    client = relationship("Client", back_populates="usage_logs")
