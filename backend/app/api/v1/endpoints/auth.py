from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.auth import Client, APIKey, APIKeyStatus, UsageLog
from app.schemas.auth import (
    ClientCreate, ClientUpdate, ClientResponse,
    APIKeyCreate, APIKeyResponse, APIKeyListItem,
    UsageLogResponse, ClientInfoResponse
)
from app.core.security import get_current_client, require_permissions
from app.core.cache import Cache

router = APIRouter()


# ============= CLIENT MANAGEMENT (Admin endpoints) =============

@router.post("/clients", response_model=ClientResponse, tags=["Admin - Clients"])
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo cliente (empresa/departamento/sistema)
    """
    # Verifica se email já existe
    existing = db.query(Client).filter(Client.email == client_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    client = Client(**client_data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client


@router.get("/clients", response_model=List[ClientResponse], tags=["Admin - Clients"])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista todos os clientes
    """
    query = db.query(Client)
    
    if is_active is not None:
        query = query.filter(Client.is_active == is_active)
    
    clients = query.offset(skip).limit(limit).all()
    return clients


@router.get("/clients/{client_id}", response_model=ClientResponse, tags=["Admin - Clients"])
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca um cliente por ID
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return client


@router.patch("/clients/{client_id}", response_model=ClientResponse, tags=["Admin - Clients"])
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza informações de um cliente
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    
    # Limpa cache das API keys deste cliente
    Cache.clear_pattern(f"api_key:client:{client_id}:*")
    
    return client


@router.delete("/clients/{client_id}", tags=["Admin - Clients"])
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta um cliente (e todas suas API keys)
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    db.delete(client)
    db.commit()
    
    # Limpa cache
    Cache.clear_pattern(f"api_key:client:{client_id}:*")
    
    return {"message": "Cliente deletado com sucesso"}


# ============= API KEY MANAGEMENT =============

@router.post("/clients/{client_id}/api-keys", response_model=APIKeyResponse, tags=["Admin - API Keys"])
async def create_api_key(
    client_id: int,
    key_data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova API Key para um cliente
    
    **IMPORTANTE**: A key completa é mostrada apenas uma vez. Guarde-a em local seguro!
    """
    # Verifica se cliente existe
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verifica limite de keys
    existing_keys = db.query(APIKey).filter(
        APIKey.client_id == client_id,
        APIKey.status == APIKeyStatus.ACTIVE
    ).count()
    
    if existing_keys >= client.max_api_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite de {client.max_api_keys} API Keys atingido"
        )
    
    # Gera a key
    prefix = "sk_live" if key_data.environment == "production" else "sk_test"
    full_key, key_hash, last_chars = APIKey.generate_key(prefix)
    
    # Calcula expiração
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Cria no DB
    api_key = APIKey(
        client_id=client_id,
        key_prefix=prefix,
        key_hash=key_hash,
        key_last_chars=last_chars,
        name=key_data.name,
        description=key_data.description,
        permissions=key_data.permissions,
        allowed_ips=key_data.allowed_ips,
        allowed_domains_ids=key_data.allowed_domains_ids,
        expires_at=expires_at
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Retorna com a key completa
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        description=api_key.description,
        key_preview=f"{api_key.key_prefix}_****{api_key.key_last_chars}",
        full_key=full_key,  # Mostrada APENAS aqui
        status=api_key.status,
        permissions=api_key.permissions,
        allowed_ips=api_key.allowed_ips,
        allowed_domains_ids=api_key.allowed_domains_ids,
        created_at=api_key.created_at,
        total_requests=0,
        expires_at=api_key.expires_at,
        warning="⚠️ IMPORTANTE: Guarde esta key em local seguro. Ela não será mostrada novamente!"
    )


@router.get("/clients/{client_id}/api-keys", response_model=List[APIKeyListItem], tags=["Admin - API Keys"])
async def list_api_keys(
    client_id: int,
    status_filter: APIKeyStatus = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista todas as API Keys de um cliente
    """
    query = db.query(APIKey).filter(APIKey.client_id == client_id)
    
    if status_filter:
        query = query.filter(APIKey.status == status_filter)
    
    keys = query.order_by(APIKey.created_at.desc()).all()
    
    return [
        APIKeyListItem(
            id=key.id,
            name=key.name,
            key_preview=f"{key.key_prefix}_****{key.key_last_chars}",
            status=key.status,
            permissions=key.permissions,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            total_requests=key.total_requests,
            expires_at=key.expires_at
        )
        for key in keys
    ]


@router.patch("/clients/{client_id}/api-keys/{key_id}/revoke", tags=["Admin - API Keys"])
async def revoke_api_key(
    client_id: int,
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    Revoga uma API Key
    """
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.client_id == client_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key não encontrada"
        )
    
    api_key.status = APIKeyStatus.REVOKED
    api_key.revoked_at = datetime.utcnow()
    db.commit()
    
    # Limpa do cache
    Cache.delete(f"api_key:{api_key.key_hash}")
    
    return {"message": "API Key revogada com sucesso"}


@router.delete("/clients/{client_id}/api-keys/{key_id}", tags=["Admin - API Keys"])
async def delete_api_key(
    client_id: int,
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta permanentemente uma API Key
    """
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.client_id == client_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key não encontrada"
        )
    
    # Limpa do cache
    Cache.delete(f"api_key:{api_key.key_hash}")
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API Key deletada com sucesso"}


# ============= AUTHENTICATED CLIENT ENDPOINTS =============

@router.get("/me", response_model=ClientInfoResponse, tags=["Client Info"])
async def get_my_info(
    auth_data: tuple = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """
    Retorna informações do cliente autenticado via API Key
    """
    client, api_key = auth_data
    
    # Estatísticas de uso
    total_requests_today = db.query(func.count(UsageLog.id)).filter(
        UsageLog.client_id == client.id,
        UsageLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).scalar()
    
    avg_response_time = db.query(func.avg(UsageLog.response_time_ms)).filter(
        UsageLog.client_id == client.id,
        UsageLog.created_at >= datetime.utcnow() - timedelta(days=7)
    ).scalar()
    
    return ClientInfoResponse(
        client=ClientResponse.model_validate(client),
        api_key_info={
            "name": api_key.name,
            "key_preview": f"{api_key.key_prefix}_****{api_key.key_last_chars}",
            "permissions": api_key.permissions,
            "total_requests": api_key.total_requests,
            "last_used": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None
        },
        usage_summary={
            "requests_today": total_requests_today or 0,
            "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else 0,
            "rate_limits": {
                "per_minute": client.rate_limit_per_minute,
                "per_day": client.rate_limit_per_day
            }
        }
    )


@router.get("/usage/logs", response_model=List[UsageLogResponse], tags=["Client Info"])
async def get_usage_logs(
    auth_data: tuple = Depends(get_current_client),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retorna logs de uso da API Key autenticada
    """
    client, api_key = auth_data
    
    logs = db.query(UsageLog).filter(
        UsageLog.client_id == client.id
    ).order_by(
        UsageLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return logs
