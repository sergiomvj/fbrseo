# API Key - Sistema VideoCreator

## 🔑 Credenciais de Acesso

### Informações do Cliente
- **Cliente ID**: `6`
- **Nome**: Sistema VideoCreator
- **Email**: videocreator@fbrapps.com
- **Empresa**: FBR Apps

### API Key de Produção

```
sk_live__iy1uOMGmSPnO6ohlhBGQi-uqKl4ipl29hEN_NZTTUk
```

> ⚠️ **IMPORTANTE**: Esta chave deve ser armazenada de forma segura e nunca commitada no repositório.

---

## 📊 Configurações e Limites

### Rate Limits
- **Por minuto**: 80 requisições
- **Por dia**: 30.000 requisições

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

Adicione no arquivo `.env` do projeto VideoCreator:

```env
# SEO API Configuration
SEO_API_URL=http://localhost:8000
SEO_API_KEY=sk_live__iy1uOMGmSPnO6ohlhBGQi-uqKl4ipl29hEN_NZTTUk
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

  // Buscar keywords para títulos de vídeos
  async getVideoKeywords(domainId) {
    return this.request(`/keywords?domain_id=${domainId}`);
  }

  // Verificar rankings de vídeos
  async checkVideoRankings(domainId) {
    return this.request(`/rankings?domain_id=${domainId}`);
  }

  // Analisar concorrentes no YouTube
  async analyzeYouTubeCompetitors(domainId) {
    return this.request(`/competitors?domain_id=${domainId}`);
  }
}

export default new SEOAPIClient();
```

### 3. Exemplo de Uso

```javascript
import seoAPI from './seo-api-client';

// Buscar keywords para títulos de vídeos
const keywords = await seoAPI.getVideoKeywords(1);
console.log('Keywords para vídeos:', keywords);

// Verificar rankings
const rankings = await seoAPI.checkVideoRankings(1);
console.log('Rankings:', rankings);
```

---

## 🧪 Teste de Conexão

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" `
  -Headers @{"X-API-Key"="sk_live__iy1uOMGmSPnO6ohlhBGQi-uqKl4ipl29hEN_NZTTUk"} `
  -UseBasicParsing
```

### cURL (Linux/Mac)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: sk_live__iy1uOMGmSPnO6ohlhBGQi-uqKl4ipl29hEN_NZTTUk"
```

---

## 📚 Endpoints Disponíveis

### Keywords
- `GET /api/v1/keywords?domain_id={id}` - Keywords para títulos/descrições
- `POST /api/v1/keywords` - Criar keyword

### Rankings
- `GET /api/v1/rankings?domain_id={id}` - Rankings de vídeos

### Competidores
- `GET /api/v1/competitors?domain_id={id}` - Análise de concorrentes

### Análise On-Page
- `GET /api/v1/onpage?url={url}` - Análise SEO

### Import
- `POST /api/v1/import/semrush/keywords?domain_id={id}` - Importar dados

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

---

## 📞 Suporte

Para questões técnicas ou problemas com a API, contate o time de infraestrutura.
