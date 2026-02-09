# API Key - Sistema TVFACEBRASIL

## 🔑 Credenciais de Acesso

### Informações do Cliente
- **Cliente ID**: `8`
- **Nome**: Sistema TVFACEBRASIL
- **Email**: tvfacebrasil@fbrapps.com
- **Empresa**: FBR Apps

### API Key de Produção

```
sk_live_...
```

> ⚠️ **IMPORTANTE**: Esta chave deve ser armazenada de forma segura e nunca commitada no repositório.

---

## 📊 Configurações e Limites

### Rate Limits
- **Por minuto**: 120 requisições
- **Por dia**: 50000 requisições

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

Adicione no arquivo `.env` do projeto TVFACEBRASIL:

```env
# SEO API Configuration
SEO_API_URL=http://seo.fbrapps.com:8000
SEO_API_KEY=sk_live_...
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
}

export default new SEOAPIClient();
```

---

## 🧪 Teste de Conexão

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://seo.fbrapps.com:8000/api/v1/auth/me" `
  -Headers @{"X-API-Key"="sk_live_..."} `
  -UseBasicParsing
```

### cURL (Linux/Mac)
```bash
curl -X GET "http://seo.fbrapps.com:8000/api/v1/auth/me" \
  -H "X-API-Key: sk_live_..."
```

---

## 📞 Suporte

Para questões técnicas ou problemas com a API, contate o time de infraestrutura.
