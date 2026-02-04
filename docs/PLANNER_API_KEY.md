# API Key - Sistema Planner

## 🔑 Credenciais de Acesso

### Informações do Cliente
- **Cliente ID**: `3`
- **Nome**: Sistema Planner
- **Email**: planner@fbrapps.com
- **Empresa**: FBR Apps

### API Key de Produção

```
<sua-api-key-planner>
```

> ⚠️ **IMPORTANTE**: Esta chave deve ser armazenada de forma segura e nunca commitada no repositório.

---

## 📊 Configurações e Limites

### Rate Limits
- **Por minuto**: 120 requisições
- **Por dia**: 50.000 requisições

### Permissões Concedidas
- ✅ `keywords:read` - Leitura de keywords
- ✅ `keywords:write` - Criação/edição de keywords
- ✅ `rankings:read` - Leitura de rankings
- ✅ `rankings:write` - Criação/edição de rankings
- ✅ `backlinks:read` - Leitura de backlinks
- ✅ `onpage:read` - Análise on-page
- ✅ `competitors:read` - Dados de concorrentes
- ✅ `data:import` - Importação de CSVs do SemRush

---

## 💻 Configuração no Projeto

### 1. Variáveis de Ambiente

Adicione no arquivo `.env` do projeto Planner:

```env
# SEO API Configuration
SEO_API_URL=http://localhost:8000
SEO_API_KEY=<sua-api-key-planner>
```

### 2. Exemplo de Integração (JavaScript/TypeScript)

```javascript
// seo-api-client.js
const SEO_API_URL = process.env.SEO_API_URL;
const SEO_API_KEY = process.env.SEO_API_KEY;

class SEOAPIClient {
  constructor() {
    this.baseURL = SEO_API_URL;
    this.apiKey = SEO_API_KEY;
  }

  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseURL}/api/v1${endpoint}`, {
      ...options,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`SEO API Error: ${response.status}`);
    }

    return response.json();
  }

  // Buscar keywords
  async getKeywords(domainId) {
    return this.request(`/keywords?domain_id=${domainId}`);
  }

  // Buscar rankings
  async getRankings(domainId) {
    return this.request(`/rankings?domain_id=${domainId}`);
  }

  // Criar domínio
  async createDomain(url, name) {
    return this.request('/domains', {
      method: 'POST',
      body: JSON.stringify({ url, name })
    });
  }
}

export default new SEOAPIClient();
```

### 3. Exemplo de Uso

```javascript
import seoAPI from './seo-api-client';

// Buscar keywords de um domínio
const keywords = await seoAPI.getKeywords(1);
console.log('Keywords:', keywords);

// Criar novo domínio
const domain = await seoAPI.createDomain('https://example.com', 'Example Site');
console.log('Domínio criado:', domain);
```

---

## 🧪 Teste de Conexão

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" `
  -Headers @{"X-API-Key"="<sua-api-key-planner>"} `
  -UseBasicParsing
```

### cURL (Linux/Mac)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: <sua-api-key-planner>"
```

---

## 📚 Endpoints Disponíveis

### Domínios
- `GET /api/v1/domains` - Listar todos os domínios
- `POST /api/v1/domains` - Criar novo domínio
- `GET /api/v1/domains/{id}` - Buscar domínio específico

### Keywords
- `GET /api/v1/keywords?domain_id={id}` - Listar keywords de um domínio
- `POST /api/v1/keywords` - Criar nova keyword
- `GET /api/v1/keywords/{id}` - Buscar keyword específica

### Rankings
- `GET /api/v1/rankings?domain_id={id}` - Listar rankings de um domínio
- `POST /api/v1/rankings` - Criar novo ranking

### Backlinks
- `GET /api/v1/backlinks?domain_id={id}` - Listar backlinks de um domínio

### Análise
- `GET /api/v1/onpage?url={url}` - Análise on-page de uma URL
- `GET /api/v1/competitors?domain_id={id}` - Dados de concorrentes

### Import
- `POST /api/v1/import/semrush/keywords?domain_id={id}` - Importar keywords do SemRush
- `POST /api/v1/import/semrush/rankings?domain_id={id}` - Importar rankings do SemRush

---

## 📖 Documentação Completa da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔒 Segurança

### Checklist de Segurança
- [ ] API Key armazenada em variável de ambiente
- [ ] Arquivo `.env` adicionado ao `.gitignore`
- [ ] Nunca expor a API Key no código frontend
- [ ] Implementar rotação periódica de chaves

### Monitoramento de Rate Limits

Todas as respostas incluem headers de rate limit:

```
X-RateLimit-Limit-Minute: 120
X-RateLimit-Remaining-Minute: 115
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 49850
```

---

## 📞 Suporte

Para questões técnicas ou problemas com a API, contate o time de infraestrutura.
