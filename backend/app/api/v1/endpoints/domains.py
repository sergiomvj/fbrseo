from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.domain import Domain
from app.schemas.seo import DomainCreate, DomainUpdate, DomainResponse
from app.core.security import get_current_client

router = APIRouter()

@router.post("/", response_model=DomainResponse, tags=["Domains"])
async def create_domain(
    domain_data: DomainCreate,
    auth_data: tuple = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Cria um novo domínio"""
    client, _ = auth_data
    
    existing = db.query(Domain).filter(Domain.url == domain_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Domínio já existe")
    
    domain = Domain(
        client_id=client.id,
        url=domain_data.url,
        name=domain_data.name
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain

@router.get("/", response_model=List[DomainResponse], tags=["Domains"])
async def list_domains(
    auth_data: tuple = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Lista domínios do cliente"""
    client, api_key = auth_data
    
    query = db.query(Domain).filter(Domain.client_id == client.id)
    
    if api_key.allowed_domains_ids:
        query = query.filter(Domain.id.in_(api_key.allowed_domains_ids))
    
    return query.all()

@router.get("/{domain_id}", response_model=DomainResponse, tags=["Domains"])
async def get_domain(
    domain_id: int,
    auth_data: tuple = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Busca um domínio"""
    client, api_key = auth_data
    
    domain = db.query(Domain).filter(
        Domain.id == domain_id,
        Domain.client_id == client.id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    
    if api_key.allowed_domains_ids and domain_id not in api_key.allowed_domains_ids:
        raise HTTPException(status_code=403, detail="Acesso negado a este domínio")
    
    return domain
