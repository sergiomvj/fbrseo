from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import datetime
from app.database import get_db
from app.models.auth import APIKey, Client, APIKeyStatus, APIKeyPermission
from app.core.cache import Cache, RateLimiter
import json

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_client(
    request: Request,
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Tuple[Client, APIKey]:
    """
    Valida API Key e retorna Client + APIKey
    """
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key não fornecida. Use o header X-API-Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # 1. Valida formato
    if not api_key.startswith("sk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de API Key inválido"
        )
    
    # 2. Hash da key
    key_hash = APIKey.hash_key(api_key)
    
    # 3. Busca no cache primeiro
    cache_key = f"api_key:{key_hash}"
    cached_data = Cache.get(cache_key)
    
    if cached_data:
        api_key_id = cached_data.get('api_key_id')
        client_id = cached_data.get('client_id')
        
        api_key_obj = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        client = db.query(Client).filter(Client.id == client_id).first()
    else:
        # Busca no DB
        api_key_obj = db.query(APIKey).filter(
            APIKey.key_hash == key_hash
        ).first()
        
        if not api_key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key inválida"
            )
        
        client = db.query(Client).filter(Client.id == api_key_obj.client_id).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cliente não encontrado"
            )
        
        # Cacheia por 5 minutos
        Cache.set(
            cache_key,
            {
                'api_key_id': api_key_obj.id,
                'client_id': client.id,
                'status': api_key_obj.status.value,
                'permissions': api_key_obj.permissions
            },
            ttl=300
        )
    
    # 4. Valida status
    if api_key_obj.status != APIKeyStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API Key está {api_key_obj.status.value}"
        )
    
    # 5. Valida expiração
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        api_key_obj.status = APIKeyStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key expirada"
        )
    
    # 6. Valida se cliente está ativo
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente inativo"
        )
    
    # 7. Valida IP (se configurado)
    if api_key_obj.allowed_ips:
        client_ip = request.client.host
        if client_ip not in api_key_obj.allowed_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"IP {client_ip} não autorizado"
            )
    
    # 8. Rate Limiting
    allowed, rate_info = RateLimiter.check_rate_limit(
        client.id,
        client.rate_limit_per_minute,
        client.rate_limit_per_day
    )
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit excedido: {rate_info.get('reason')}",
            headers={
                "X-RateLimit-Limit-Minute": str(client.rate_limit_per_minute),
                "X-RateLimit-Limit-Day": str(client.rate_limit_per_day),
                "X-RateLimit-Remaining-Minute": str(rate_info.get('remaining_minute', 0)),
                "X-RateLimit-Remaining-Day": str(rate_info.get('remaining_day', 0)),
            }
        )
    
    # 9. Atualiza last_used (de forma assíncrona/periódica para não travar)
    api_key_obj.last_used_at = datetime.utcnow()
    api_key_obj.total_requests += 1
    db.commit()
    
    # 10. Armazena no request state para uso no middleware de logging
    request.state.client_id = client.id
    request.state.api_key_id = api_key_obj.id
    
    return client, api_key_obj


def require_permissions(required_permissions: List[str]):
    """
    Dependency para verificar permissões específicas
    """
    async def permission_checker(
        auth_data: Tuple[Client, APIKey] = Depends(get_current_client)
    ) -> Tuple[Client, APIKey]:
        client, api_key = auth_data
        
        # Admin tem acesso total
        if APIKeyPermission.ADMIN_FULL.value in api_key.permissions:
            return client, api_key
        
        # Verifica permissões específicas
        missing_permissions = []
        for perm in required_permissions:
            if perm not in api_key.permissions:
                missing_permissions.append(perm)
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissões necessárias: {', '.join(missing_permissions)}"
            )
        
        return client, api_key
    
    return permission_checker


def check_domain_access(domain_id: int, api_key: APIKey) -> bool:
    """
    Verifica se a API Key tem acesso ao domínio
    """
    # Se não há restrição de domínios, permite acesso
    if not api_key.allowed_domains_ids:
        return True
    
    # Verifica se o domínio está na lista permitida
    return domain_id in api_key.allowed_domains_ids


async def verify_domain_access(
    domain_id: int,
    auth_data: Tuple[Client, APIKey] = Depends(get_current_client)
) -> Tuple[Client, APIKey]:
    """
    Dependency para verificar acesso a um domínio específico
    """
    client, api_key = auth_data
    
    if not check_domain_access(domain_id, api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso ao domínio {domain_id} não autorizado para esta API Key"
        )
    
    return client, api_key
