"""
SEO API Python SDK
==================

Cliente Python oficial para integração com a SEO API.

Uso básico:
    from seo_api import SEOClient
    
    client = SEOClient(
        base_url="http://localhost:8000",
        api_key="sk_live_xxxxx"
    )
    
    # Criar domínio
    domain = client.domains.create(url="https://site.com", name="Meu Site")
"""

from .client import SEOClient
from .exceptions import SEOAPIError, AuthenticationError, RateLimitError, NotFoundError

__version__ = "1.0.0"
__all__ = ["SEOClient", "SEOAPIError", "AuthenticationError", "RateLimitError", "NotFoundError"]
