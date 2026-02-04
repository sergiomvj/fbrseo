"""
Exceções customizadas para SEO API
"""


class SEOAPIError(Exception):
    """Erro base da SEO API"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(self.message)


class AuthenticationError(SEOAPIError):
    """Erro de autenticação (401/403)"""
    pass


class RateLimitError(SEOAPIError):
    """Rate limit excedido (429)"""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class NotFoundError(SEOAPIError):
    """Recurso não encontrado (404)"""
    pass


class ValidationError(SEOAPIError):
    """Erro de validação (422)"""
    pass
