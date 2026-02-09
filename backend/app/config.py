from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente
    """
    
    # Database
    DATABASE_URL: str = "sqlite:////data/app.db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SEO API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str = "insecure-default-key-please-change"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 60
    DEFAULT_RATE_LIMIT_PER_DAY: int = 10000
    
    # Google APIs
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # External APIs (opcionais)
    DATAFORSEO_LOGIN: Optional[str] = None
    DATAFORSEO_PASSWORD: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@seoapi.com"
    EMAILS_FROM_NAME: str = "SEO API"
    
    # Crawler
    CRAWLER_USER_AGENT: str = "SEO-API-Bot/1.0"
    CRAWLER_MAX_CONCURRENT: int = 10
    CRAWLER_DELAY_SECONDS: float = 1.0
    
    # Firecrawl
    FIRECRAWL_API_URL: Optional[str] = None
    FIRECRAWL_API_KEY: Optional[str] = None
    
    # Storage
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cache das configurações
    """
    return Settings()


settings = get_settings()
