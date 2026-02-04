# 🚀 Guia de Início Rápido

## Opção 1: Setup Automático (Recomendado)

```bash
./setup.sh
```

O script irá:
1. Verificar Docker
2. Criar arquivo .env
3. Iniciar os serviços
4. Criar um cliente de exemplo

## Opção 2: Setup Manual

### 1. Configurar ambiente

```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` e configure:
- `SECRET_KEY` - Chave secreta única
- Outras configurações conforme necessário

### 2. Iniciar serviços

```bash
docker-compose up -d
```

### 3. Verificar se está funcionando

```bash
# Testar API
curl http://localhost:8000/health

# Ver logs
docker-compose logs -f backend
```

## Primeiros Passos

### 1. Criar um Cliente

Acesse `http://localhost:8000/docs` e use o endpoint POST `/api/v1/auth/clients`:

```json
{
  "name": "Marketing Team",
  "company": "Minha Empresa",
  "email": "marketing@empresa.com",
  "rate_limit_per_minute": 60,
  "rate_limit_per_day": 10000
}
```

Anote o `id` retornado (ex: 1).

### 2. Criar API Key

Use POST `/api/v1/auth/clients/{client_id}/api-keys`:

```json
{
  "name": "Production API",
  "environment": "production",
  "permissions": [
    "keywords:read",
    "rankings:read",
    "backlinks:read",
    "data:import",
    "admin:*"
  ]
}
```

**⚠️ IMPORTANTE**: Copie o `full_key` retornado. Exemplo:
```
<sua-api-key-de-producao>
```

### 3. Testar API Key

```bash
export API_KEY="sk_live_sua_key_aqui"

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: $API_KEY"
```

### 4. Criar um Domínio

```bash
curl -X POST "http://localhost:8000/api/v1/domains" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://meusite.com",
    "name": "Meu Site"
  }'
```

### 5. Importar Dados do SemRush

Exporte keywords do SemRush em formato CSV, depois:

```bash
curl -X POST "http://localhost:8000/api/v1/import/semrush/keywords?domain_id=1" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@keywords.csv"
```

## Estrutura de CSV do SemRush

### Keywords CSV
Colunas esperadas:
- Keyword
- Search Volume
- Keyword Difficulty (ou KD%)
- CPC
- Competition
- Position (opcional)
- URL (opcional)

### Rankings CSV
Colunas esperadas:
- Keyword
- Position
- Previous Position
- URL
- Traffic %

### Backlinks CSV
Colunas esperadas:
- Source URL
- Target URL
- Referring Domain
- Authority Score
- Anchor
- Type (follow/nofollow)
- First Seen
- Last Seen

## Endpoints Principais

### Autenticação
- `POST /api/v1/auth/clients` - Criar cliente
- `POST /api/v1/auth/clients/{id}/api-keys` - Criar API key
- `GET /api/v1/auth/me` - Info do cliente autenticado

### Domínios
- `POST /api/v1/domains` - Criar domínio
- `GET /api/v1/domains` - Listar domínios
- `GET /api/v1/domains/{id}` - Buscar domínio

### Import
- `POST /api/v1/import/semrush/keywords` - Import keywords
- `POST /api/v1/import/semrush/rankings` - Import rankings
- `POST /api/v1/import/semrush/backlinks` - Import backlinks

## Troubleshooting

### "Connection refused" ao acessar API
```bash
# Verificar se containers estão rodando
docker-compose ps

# Reiniciar serviços
docker-compose restart
```

### "Database connection error"
```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Recriar banco
docker-compose down -v
docker-compose up -d
```

### API Key inválida
- Verifique se copiou a key completa
- Confirme que está usando o header `X-API-Key`
- Verifique se a key não foi revogada

## Comandos Úteis

```bash
# Ver todos os logs
docker-compose logs -f

# Ver logs apenas do backend
docker-compose logs -f backend

# Parar tudo
docker-compose down

# Parar e remover volumes (⚠️ apaga dados)
docker-compose down -v

# Rebuild após mudanças
docker-compose up -d --build

# Acessar banco de dados
docker-compose exec postgres psql -U seo_user -d seo_api_db

# Acessar Redis
docker-compose exec redis redis-cli
```

## Próximos Passos

1. **Configurar Google Search Console**
   - Obter credentials.json
   - Configurar em backend/.env
   - Ativar sync automático

2. **Configurar Google Analytics**
   - Similar ao GSC
   - Dados de tráfego real

3. **Automatizar import do SemRush**
   - Script para export automático
   - Cron job para upload

4. **Explorar Dashboard Frontend**
   - Acesse http://localhost:3000
   - Visualize dados
   - Gerencie API keys

## Documentação Completa

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- README completo: `README.md`
