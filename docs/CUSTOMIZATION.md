# 🛠️ Guia de Customização - SEO API

Este documento explica como customizar e estender a SEO API após descompactar no Antigravity.

## 📦 Conteúdo do Pacote

```
seo-api-project/
├── backend/              # API FastAPI
├── frontend/             # Dashboard React
├── docker-compose.yml    # Orquestração Docker
├── setup.sh             # Script de setup automático
├── README.md            # Documentação completa
├── QUICK_START.md       # Guia de início rápido
└── CUSTOMIZATION.md     # Este arquivo
```

## 🔧 Customizações Comuns

### 1. Adicionar Novos Endpoints

**Localização**: `backend/app/api/v1/endpoints/`

Exemplo - Adicionar endpoint de keywords:

```python
# backend/app/api/v1/endpoints/keywords.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_client, require_permissions
from app.models.auth import APIKeyPermission

router = APIRouter()

@router.get("/{domain_id}/keywords")
async def get_keywords(
    domain_id: int,
    auth_data: tuple = Depends(require_permissions([APIKeyPermission.READ_KEYWORDS.value])),
    db: Session = Depends(get_db)
):
    """Lista keywords de um domínio"""
    client, api_key = auth_data
    # Sua lógica aqui
    return {"keywords": []}
```

Depois registre no router principal:

```python
# backend/app/api/v1/__init__.py
from app.api.v1.endpoints import keywords

router.include_router(keywords.router, prefix="/keywords", tags=["Keywords"])
```

### 2. Adicionar Novos Models

**Localização**: `backend/app/models/`

Exemplo - Model de Competitor:

```python
# backend/app/models/competitor.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    competitor_url = Column(String(255))
    # Adicione mais campos...
```

Registre no `__init__.py`:

```python
# backend/app/models/__init__.py
from app.models.competitor import Competitor

__all__ = [..., "Competitor"]
```

### 3. Integrar API Externa (DataForSEO)

**Localização**: `backend/app/services/external/`

Crie o serviço:

```python
# backend/app/services/external/dataforseo.py
import httpx
from app.config import settings

class DataForSEOService:
    BASE_URL = "https://api.dataforseo.com/v3"
    
    def __init__(self):
        self.login = settings.DATAFORSEO_LOGIN
        self.password = settings.DATAFORSEO_PASSWORD
    
    async def get_keyword_data(self, keyword: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/keywords_data/google/search_volume/live",
                auth=(self.login, self.password),
                json=[{"keywords": [keyword]}]
            )
            return response.json()
```

Use no endpoint:

```python
from app.services.external.dataforseo import DataForSEOService

@router.get("/keyword/enriched")
async def get_enriched_keyword(keyword: str):
    service = DataForSEOService()
    data = await service.get_keyword_data(keyword)
    return data
```

### 4. Adicionar Jobs Celery

**Localização**: `backend/app/tasks/`

Crie o Celery app:

```python
# backend/app/tasks/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "seo_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    'app.tasks.crawl_tasks.*': {'queue': 'crawl'},
}
```

Crie tasks:

```python
# backend/app/tasks/ranking_tasks.py
from app.tasks.celery_app import celery_app
from app.database import SessionLocal

@celery_app.task
def update_rankings_daily(domain_id: int):
    """Atualiza rankings diariamente"""
    db = SessionLocal()
    try:
        # Sua lógica aqui
        pass
    finally:
        db.close()
```

Agende no celery beat:

```python
celery_app.conf.beat_schedule = {
    'update-rankings-daily': {
        'task': 'app.tasks.ranking_tasks.update_rankings_daily',
        'schedule': crontab(hour=2, minute=0),  # 2 AM diariamente
    },
}
```

### 5. Customizar Frontend - Adicionar Nova Página

**Localização**: `frontend/src/pages/`

Crie a página:

```javascript
// frontend/src/pages/Keywords.js
import React, { useEffect, useState } from 'react';
import { Container, Typography, CircularProgress } from '@mui/material';
import { domainsAPI } from '../services/api';

function Keywords() {
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKeywords();
  }, []);

  const fetchKeywords = async () => {
    try {
      const response = await domainsAPI.getKeywords(1); // domain_id
      setKeywords(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Container>
      <Typography variant="h3">Keywords</Typography>
      {/* Sua UI aqui */}
    </Container>
  );
}

export default Keywords;
```

Adicione à rota:

```javascript
// frontend/src/App.js
import Keywords from './pages/Keywords';

// No <Routes>:
<Route path="/keywords" element={<Keywords />} />
```

### 6. Adicionar Nova Permissão

**Localização**: `backend/app/models/auth.py`

```python
class APIKeyPermission(str, enum.Enum):
    # ... existentes
    READ_ANALYTICS = "analytics:read"
    WRITE_ANALYTICS = "analytics:write"
```

Use nos endpoints:

```python
@router.get("/analytics")
async def get_analytics(
    auth = Depends(require_permissions([APIKeyPermission.READ_ANALYTICS.value]))
):
    pass
```

### 7. Implementar Crawler On-Page

**Localização**: `backend/app/services/crawler/`

```python
# backend/app/services/crawler/onpage_analyzer.py
from bs4 import BeautifulSoup
import httpx

class OnPageAnalyzer:
    
    async def analyze_page(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'title': soup.find('title').text if soup.find('title') else None,
                'meta_description': self._get_meta_description(soup),
                'h1': soup.find('h1').text if soup.find('h1') else None,
                'word_count': len(soup.get_text().split()),
                'images': len(soup.find_all('img')),
                # Adicione mais análises...
            }
    
    def _get_meta_description(self, soup):
        meta = soup.find('meta', {'name': 'description'})
        return meta.get('content') if meta else None
```

### 8. Adicionar Importador de CSV

**Localização**: `backend/app/services/importers/`

```python
# backend/app/services/importers/semrush_importer.py
import pandas as pd
from app.models.domain import Keyword

class SemRushImporter:
    
    def import_keywords(self, csv_path: str, domain_id: int, db):
        df = pd.read_csv(csv_path)
        
        keywords = []
        for _, row in df.iterrows():
            kw = Keyword(
                domain_id=domain_id,
                keyword=row['Keyword'],
                search_volume=row.get('Search Volume', 0),
                keyword_difficulty=row.get('Keyword Difficulty', 0),
                cpc=row.get('CPC', 0),
                source='semrush'
            )
            keywords.append(kw)
        
        db.bulk_save_objects(keywords)
        db.commit()
        return len(keywords)
```

## 🚀 Deploy em Produção

### 1. Variáveis de Ambiente

Edite `backend/.env` para produção:

```env
DEBUG=False
SECRET_KEY=gere-uma-chave-super-segura-aqui
DATABASE_URL=postgresql://user:pass@seu-servidor:5432/db
ALLOWED_HOSTS=["seu-dominio.com"]
CORS_ORIGINS=["https://seu-frontend.com"]
```

### 2. SSL/HTTPS

Configure nginx como reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name api.seudominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Banco de Dados

Use PostgreSQL gerenciado (RDS, Cloud SQL, etc):

```bash
# Dump do banco local
docker-compose exec postgres pg_dump -U seo_user seo_api_db > backup.sql

# Restore em produção
psql -h prod-server -U user -d db < backup.sql
```

### 4. Monitoramento

Configure Sentry para erros:

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment="production"
)
```

## 📞 Suporte

Para dúvidas sobre customização:
- Consulte a documentação da API: `/docs`
- Veja exemplos nos arquivos existentes
- Stack: FastAPI, SQLAlchemy, React, MUI

## ✅ Checklist de Customização

- [ ] Ler README.md completo
- [ ] Seguir QUICK_START.md
- [ ] Testar localmente com Docker
- [ ] Adicionar seus endpoints
- [ ] Implementar integrações necessárias
- [ ] Customizar frontend conforme brand
- [ ] Configurar variáveis de produção
- [ ] Testar em staging
- [ ] Deploy em produção

Boa sorte com suas customizações! 🚀
