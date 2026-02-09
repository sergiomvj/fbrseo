# 🔑 SEO API - Credenciais de Integração

Documento consolidado com todas as API Keys para integração dos sistemas FBR Apps com o SEO API.

---

## 📋 Visão Geral

| Sistema | Cliente ID | Email | Rate Limit/min | Rate Limit/dia | Documentação |
|---------|-----------|-------|----------------|----------------|--------------|
| **Planner** | 3 | planner@fbrapps.com | 120 | 50.000 | [PLANNER_API_KEY.md](PLANNER_API_KEY.md) |
| **Blogger** | 4 | blogger@fbrapps.com | 100 | 40.000 | [BLOGGER_API_KEY.md](BLOGGER_API_KEY.md) |
| **Creator** | 5 | creator@fbrapps.com | 100 | 40.000 | [CREATOR_API_KEY.md](CREATOR_API_KEY.md) |
| **VideoCreator** | 6 | videocreator@fbrapps.com | 80 | 30.000 | [VIDEOCREATOR_API_KEY.md](VIDEOCREATOR_API_KEY.md) |
| **FACEBRASIL** | 7 | facebrasil@fbrapps.com | 120 | 50.000 | [FACEBRASIL_API_KEY.md](FACEBRASIL_API_KEY.md) |
| **TVFACEBRASIL** | 8 | tvfacebrasil@fbrapps.com | 120 | 50.000 | [TVFACEBRASIL_API_KEY.md](TVFACEBRASIL_API_KEY.md) |

---

## 🔐 API Keys

### Sistema Planner
```
<sua-api-key-planner>
```

### Sistema Blogger
```
<sua-api-key-blogger>
```

### Sistema Creator
```
<sua-api-key-creator>
```

### Sistema VideoCreator
```
<sua-api-key-videocreator>
```

### Sistema FACEBRASIL
```
sk_live_...
```

### Sistema TVFACEBRASIL
```
sk_live_...
```

---

## 🚀 Configuração Rápida

### 1. Adicionar ao .env

```env
# SEO API Configuration
SEO_API_URL=http://seo.fbrapps.com:8000
SEO_API_KEY=<sua-api-key-aqui>
```

### 2. Cliente JavaScript/TypeScript

```javascript
const SEO_API_URL = process.env.SEO_API_URL;
const SEO_API_KEY = process.env.SEO_API_KEY;

async function callSEOAPI(endpoint, options = {}) {
  const response = await fetch(`${SEO_API_URL}/api/v1${endpoint}`, {
    ...options,
    headers: {
      'X-API-Key': SEO_API_KEY,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
  
  if (!response.ok) {
    throw new Error(`SEO API Error: ${response.status}`);
  }
  
  return response.json();
}
```

---

## 🎯 Permissões (Todas as API Keys)

- ✅ `keywords:read` - Leitura de keywords
- ✅ `keywords:write` - Criação/edição de keywords
- ✅ `rankings:read` - Leitura de rankings
- ✅ `rankings:write` - Criação/edição de rankings
- ✅ `backlinks:read` - Leitura de backlinks
- ✅ `onpage:read` - Análise on-page
- ✅ `competitors:read` - Dados de concorrentes
- ✅ `data:import` - Importação de CSVs

---

## 📚 Endpoints Principais

### Autenticação
- `GET /api/v1/auth/me` - Verificar autenticação

### Domínios
- `GET /api/v1/domains` - Listar domínios
- `POST /api/v1/domains` - Criar domínio
- `GET /api/v1/domains/{id}` - Buscar domínio

### Keywords
- `GET /api/v1/keywords?domain_id={id}` - Listar keywords
- `POST /api/v1/keywords` - Criar keyword

### Rankings
- `GET /api/v1/rankings?domain_id={id}` - Listar rankings
- `POST /api/v1/rankings` - Criar ranking

### Backlinks
- `GET /api/v1/backlinks?domain_id={id}` - Listar backlinks

### Análise
- `GET /api/v1/onpage?url={url}` - Análise on-page
- `GET /api/v1/competitors?domain_id={id}` - Análise de concorrentes

### Import
- `POST /api/v1/import/semrush/keywords?domain_id={id}` - Importar keywords
- `POST /api/v1/import/semrush/rankings?domain_id={id}` - Importar rankings
- `POST /api/v1/import/semrush/backlinks?domain_id={id}` - Importar backlinks

---

## 📖 Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔒 Segurança

### Checklist Obrigatório

- [ ] API Keys armazenadas em variáveis de ambiente
- [ ] Arquivo `.env` adicionado ao `.gitignore`
- [ ] Nunca expor API Keys no código frontend
- [ ] Implementar rotação periódica de chaves
- [ ] Monitorar rate limits

### Exemplo .gitignore

```gitignore
# Environment variables
.env
.env.local
.env.production
.env.*.local
```

---

## 📊 Monitoramento de Rate Limits

Headers de resposta incluem informações sobre rate limits:

```
X-RateLimit-Limit-Minute: 120
X-RateLimit-Remaining-Minute: 115
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 49850
```

---

## 🧪 Teste de Validação

```powershell
# Testar todas as API Keys
$apiKeys = @(
    @{name="Planner"; key="<sua-api-key-planner>"},
    @{name="Blogger"; key="<sua-api-key-blogger>"},
    @{name="Creator"; key="<sua-api-key-creator>"},
    @{name="VideoCreator"; key="<sua-api-key-videocreator>"},
    @{name="FACEBRASIL"; key="sk_live_..."},
    @{name="TVFACEBRASIL"; key="sk_live_..."}
)

foreach ($item in $apiKeys) {
    Write-Host "Testando $($item.name)..."
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" `
        -Headers @{"X-API-Key"=$item.key} -UseBasicParsing
}
```

---

## 📞 Suporte

Para questões técnicas ou problemas com a API:
- Documentação completa: Consulte os arquivos individuais de cada sistema
- Swagger UI: http://localhost:8000/docs
- Contato: Time de Infraestrutura FBR Apps
