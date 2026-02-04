"""
Cliente principal da SEO API
"""
import httpx
from typing import Optional, Dict, Any
from .exceptions import SEOAPIError, AuthenticationError, RateLimitError, NotFoundError, ValidationError
from .modules.domains import DomainsModule
from .modules.keywords import KeywordsModule
from .modules.imports import ImportsModule
from .modules.auth import AuthModule


class SEOClient:
    """
    Cliente principal para interagir com a SEO API.
    
    Args:
        base_url: URL base da API (ex: http://localhost:8000)
        api_key: Chave de API (ex: sk_live_xxxxx)
        timeout: Timeout em segundos (default: 30)
        max_retries: Número máximo de retentativas (default: 3)
    
    Exemplo:
        client = SEOClient(
            base_url="http://localhost:8000",
            api_key="sk_live_xxxxx"
        )
        
        domains = client.domains.list()
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configurar cliente HTTP
        self._http_client = httpx.Client(
            base_url=f"{self.base_url}/api/v1",
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "SEO-API-Python-SDK/1.0.0"
            },
            timeout=timeout
        )
        
        # Inicializar módulos
        self.auth = AuthModule(self)
        self.domains = DomainsModule(self)
        self.keywords = KeywordsModule(self)
        self.imports = ImportsModule(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa uma requisição HTTP.
        
        Args:
            method: Método HTTP (GET, POST, PATCH, DELETE)
            endpoint: Endpoint da API (ex: /domains)
            params: Query parameters
            json: Body JSON
            data: Form data
            files: Files para upload
        
        Returns:
            Resposta da API como dicionário
        
        Raises:
            AuthenticationError: Se API Key inválida
            RateLimitError: Se rate limit excedido
            NotFoundError: Se recurso não encontrado
            SEOAPIError: Para outros erros
        """
        # Remover Content-Type para uploads
        headers = {}
        if files:
            headers = {"Content-Type": None}
        
        try:
            response = self._http_client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=headers if headers else None
            )
            
            # Tratar erros
            if response.status_code == 401:
                raise AuthenticationError(
                    "API Key inválida ou não fornecida",
                    status_code=401,
                    response=response.json() if response.text else {}
                )
            
            if response.status_code == 403:
                raise AuthenticationError(
                    response.json().get("detail", "Acesso negado"),
                    status_code=403,
                    response=response.json()
                )
            
            if response.status_code == 404:
                raise NotFoundError(
                    response.json().get("detail", "Recurso não encontrado"),
                    status_code=404,
                    response=response.json()
                )
            
            if response.status_code == 422:
                raise ValidationError(
                    response.json().get("detail", "Erro de validação"),
                    status_code=422,
                    response=response.json()
                )
            
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    response.json().get("detail", "Rate limit excedido"),
                    status_code=429,
                    retry_after=int(retry_after) if retry_after else None,
                    response=response.json()
                )
            
            response.raise_for_status()
            
            # Retornar JSON ou vazio
            if response.text:
                return response.json()
            return {}
            
        except httpx.HTTPStatusError as e:
            raise SEOAPIError(
                f"Erro HTTP: {e}",
                status_code=e.response.status_code if e.response else None
            )
        except httpx.RequestError as e:
            raise SEOAPIError(f"Erro de conexão: {e}")
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Executa GET"""
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Executa POST"""
        return self._request("POST", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Executa PATCH"""
        return self._request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Executa DELETE"""
        return self._request("DELETE", endpoint, **kwargs)
    
    def close(self):
        """Fecha conexões"""
        self._http_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
