# SEO API - Sistema Completo de Análise de SEO

API completa para gerenciamento de dados de SEO com autenticação via API Keys, suporte a múltiplos clientes, e integração híbrida com SemRush + APIs gratuitas (Google Search Console, Analytics).

## 🚀 Características

### Backend (FastAPI)
- ✅ **Autenticação via API Keys** - Sistema multi-tenant seguro
- ✅ **Rate Limiting** - Controle por minuto e por dia
- ✅ **Permissões Granulares** - Controle fino de acesso
- ✅ **Cache Redis** - Performance otimizada
- ✅ **Logs Detalhados** - Auditoria completa
- ✅ **Import SemRush CSV** - Dados históricos
- ✅ **APIs Gratuitas** - Google Search Console, Analytics
- ✅ **Análise On-Page** - Crawler integrado
- ✅ **RESTful API** - Documentação automática (Swagger)

### Frontend (React)
- ✅ **Dashboard Admin** - Gerenciamento de clientes e keys
- ✅ **Visualizações** - Gráficos e métricas
- ✅ **Gerenciamento de Domínios**
- ✅ **Upload de CSV** - Import de dados do SemRush
- ✅ **Logs de Uso** - Monitoramento em tempo real

## 📋 Pré-requisitos

- Docker & Docker Compose
- OU Python 3.11+ e PostgreSQL 15+

## 🛠️ Instalação Rápida com Docker

```bash
# 1. Clone ou extraia o projeto
cd seo-api-project

# 2. Configure variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações

# 3. Inicie os serviços
docker-compose up -d

# 4. Acesse a aplicação
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

## 🔧 Instalação Manual

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Edite as variáveis conforme necessário

# Rodar migrações (criar tabelas)
python -m alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis
cp .env.example .env.local

# Iniciar dev server
npm start
```

## 📚 Uso da API

### 1. Criar um Cliente

```bash
curl -X POST "http://localhost:8000/api/v1/auth/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marketing Team",
    "company": "Minha Empresa",
    "email": "marketing@empresa.com",
    "rate_limit_per_minute": 60,
    "rate_limit_per_day": 10000
  }'
```

### 2. Criar API Key

```bash
curl -X POST "http://localhost:8000/api/v1/auth/clients/1/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Key",
    "environment": "production",
    "permissions": [
      "keywords:read",
      "rankings:read",
      "backlinks:read",
      "data:import"
    ]
  }'
```

**⚠️ IMPORTANTE**: A API Key completa é mostrada apenas uma vez. Guarde-a!

### 3. Usar a API Key

```bash
# Testar autenticação
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: sk_live_XXXXXXXXXXXXXXXX"

# Criar domínio
curl -X POST "http://localhost:8000/api/v1/domains" \
  -H "X-API-Key: sk_live_XXXXXXXXXXXXXXXX" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://meusite.com",
    "name": "Meu Site Principal"
  }'

# Importar dados do SemRush
curl -X POST "http://localhost:8000/api/v1/import/semrush/keywords?domain_id=1" \
  -H "X-API-Key: sk_live_XXXXXXXXXXXXXXXX" \
  -F "file=@keywords_export.csv"
```

## 🔐 Sistema de Permissões

### Permissões Disponíveis

- `keywords:read` - Ler keywords
- `keywords:write` - Criar/editar keywords
- `rankings:read` - Ler rankings
- `rankings:write` - Criar/editar rankings
- `backlinks:read` - Ler backlinks
- `onpage:read` - Análise on-page
- `competitors:read` - Dados de concorrentes
- `data:import` - Importar CSVs
- `admin:*` - Acesso total

## 📊 Cenário Híbrido (SemRush + APIs Free)

### Como Funciona

1. **Exportar CSVs do SemRush** (mensal/semanal)
   - Keywords com volume, difficulty, CPC
   - Rankings históricos
   - Backlinks

2. **Upload via API**
   ```bash
   POST /api/v1/import/semrush/keywords
   POST /api/v1/import/semrush/rankings
   POST /api/v1/import/semrush/backlinks
   ```

3. **Enriquecimento Automático**
   - Google Search Console (dados reais diários)
   - Google Analytics (tráfego)
   - Combina com dados do SemRush

4. **Resultado**
   - Dados históricos (SemRush)
   - Dados frescos (GSC/Analytics)
   - Score: 75/100 (vs 45/100 só free, 85/100 só pago)

## 🗂️ Estrutura do Projeto

```
seo-api-project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # Endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Lógica de negócio
│   │   ├── core/           # Config, security, cache
│   │   └── middleware/     # Logging, etc
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Páginas
│   │   ├── services/      # API client
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔄 Workflow Recomendado

1. **Setup Inicial**
   - Criar cliente no sistema
   - Gerar API Key
   - Configurar domínios

2. **Import Inicial (SemRush)**
   - Exportar CSVs
   - Upload via API ou Dashboard
   - Popular banco de dados

3. **Automação Diária**
   - Celery job: Google Search Console
   - Celery job: Google Analytics
   - Enriquecimento automático

4. **Atualização Mensal (SemRush)**
   - Novo export
   - Re-upload
   - Dados históricos atualizados

## 📈 Rate Limits

Configurável por cliente:
- **Por minuto**: padrão 60 requests
- **Por dia**: padrão 10.000 requests

Headers de resposta:
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Day: 10000
X-RateLimit-Remaining-Day: 9823
```

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar logs
docker-compose logs backend

# Verificar conexão com DB
docker-compose exec postgres psql -U seo_user -d seo_api_db
```

### Redis não conecta
```bash
# Testar conexão
docker-compose exec redis redis-cli ping
# Deve retornar: PONG
```

### Erro de permissão na API
- Verificar se API Key está ativa
- Confirmar permissões corretas
- Checar domínios permitidos (allowed_domains_ids)

## 🔒 Segurança

- API Keys hasheadas (SHA256)
- Rate limiting com Redis
- Validação de IP (opcional)
- Logs de auditoria completos
- Permissões granulares
- CORS configurável

## 📝 Documentação da API

Acesse `http://localhost:8000/docs` para documentação interativa (Swagger UI).

Ou `http://localhost:8000/redoc` para documentação alternativa (ReDoc).

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

## 📧 Suporte

Para questões e suporte, contate: suporte@empresa.com

---

**Desenvolvido com ❤️ para otimização de SEO**
