import argparse
import secrets
import hashlib
import os
import json
from datetime import datetime

# Configuration
DOCS_DIR = "docs"
API_VERSION = "v1"
BASE_URL = "http://seo.fbrapps.com:8000" # Updated to match the overview doc

# Templates
MARKDOWN_TEMPLATE = """# API Key - Sistema {system_name}

## 🔑 Credenciais de Acesso

### Informações do Cliente
- **Cliente ID**: `{client_id}`
- **Nome**: Sistema {system_name}
- **Email**: {email}
- **Empresa**: FBR Apps

### API Key de Produção

```
{api_key}
```

> ⚠️ **IMPORTANTE**: Esta chave deve ser armazenada de forma segura e nunca commitada no repositório.

---

## 📊 Configurações e Limites

### Rate Limits
- **Por minuto**: {rate_limit_min} requisições
- **Por dia**: {rate_limit_day} requisições

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

Adicione no arquivo `.env` do projeto {system_name}:

```env
# SEO API Configuration
SEO_API_URL={base_url}
SEO_API_KEY={api_key}
```

### 2. Exemplo de Integração (JavaScript/TypeScript)

```javascript
// seo-api-client.js
const SEO_API_URL = process.env.SEO_API_URL;
const SEO_API_KEY = process.env.SEO_API_KEY;

class SEOAPIClient {{
  constructor() {{
    this.baseURL = SEO_API_URL;
    this.apiKey = SEO_API_KEY;
  }}

  async request(endpoint, options = {{}}) {{
    const response = await fetch(`${{this.baseURL}}/api/v1${{endpoint}}`, {{
      ...options,
      headers: {{
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }}
    }});

    if (!response.ok) {{
      throw new Error(`SEO API Error: ${{response.status}}`);
    }}

    return response.json();
  }}
}}

export default new SEOAPIClient();
```

---

## 🧪 Teste de Conexão

### PowerShell
```powershell
Invoke-WebRequest -Uri "{base_url}/api/v1/auth/me" `
  -Headers @{{"X-API-Key"="{api_key}"}} `
  -UseBasicParsing
```

### cURL (Linux/Mac)
```bash
curl -X GET "{base_url}/api/v1/auth/me" \\
  -H "X-API-Key: {api_key}"
```

---

## 📞 Suporte

Para questões técnicas ou problemas com a API, contate o time de infraestrutura.
"""

SQL_TEMPLATE = """
-- Inserir Cliente
INSERT INTO clients (id, name, company, email, is_active, max_api_keys, rate_limit_per_minute, rate_limit_per_day, created_at, updated_at)
VALUES ({client_id}, 'Sistema {system_name}', 'FBR Apps', '{email}', true, 5, {rate_limit_min}, {rate_limit_day}, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Inserir API Key
INSERT INTO api_keys (client_id, key_prefix, key_hash, key_last_chars, name, description, status, permissions, created_at, total_requests, allowed_ips, allowed_domains_ids)
VALUES ({client_id}, '{key_prefix}', '{key_hash}', '{key_last_chars}', 'Production Key - {system_name}', 'Chave gerada automaticamente via script', 'active', '{permissions_json}', NOW(), 0, null, null);
"""

def generate_key(prefix: str = "sk_live") -> tuple:
    """
    Gera uma nova API key secure
    Returns: (full_key, key_hash, last_4_chars)
    """
    random_part = secrets.token_urlsafe(32)
    full_key = f"{prefix}_{random_part}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    last_chars = full_key[-4:]
    
    return full_key, key_hash, last_chars

def main():
    parser = argparse.ArgumentParser(description="Gerador de Cliente e API Key SEO API")
    parser.add_argument("--name", required=True, help="Nome do sistema (ex: FACEBRASIL)")
    parser.add_argument("--id", type=int, required=True, help="ID do cliente")
    parser.add_argument("--email", required=True, help="Email de contato")
    parser.add_argument("--rate-limit-min", type=int, default=120, help="Rate limit por minuto")
    parser.add_argument("--rate-limit-day", type=int, default=50000, help="Rate limit por dia")
    
    args = parser.parse_args()
    
    system_name = args.name
    client_id = args.id
    email = args.email
    
    # Gerar Key
    full_key, key_hash, last_chars = generate_key()
    prefix = full_key.split('_')[0] + "_" + full_key.split('_')[1] # sk_live
    
    # Permissions standard
    permissions = [
        "keywords:read", "keywords:write",
        "rankings:read", "rankings:write",
        "backlinks:read", "onpage:read",
        "competitors:read", "data:import"
    ]
    permissions_json = json.dumps(permissions)
    
    # Gerar Markdown
    md_content = MARKDOWN_TEMPLATE.format(
        system_name=system_name,
        client_id=client_id,
        email=email,
        api_key=full_key,
        rate_limit_min=args.rate_limit_min,
        rate_limit_day=args.rate_limit_day,
        base_url=BASE_URL,
        permissions_json=permissions_json
    )
    
    filename = f"{system_name.upper()}_API_KEY.md"
    filepath = os.path.join(DOCS_DIR, filename)
    
    # Ensure docs dir exists
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"✅ Documentação gerada em: {filepath}")
    
    # Gerar SQL
    sql_content = SQL_TEMPLATE.format(
        client_id=client_id,
        system_name=system_name,
        email=email,
        rate_limit_min=args.rate_limit_min,
        rate_limit_day=args.rate_limit_day,
        key_prefix="sk_live",
        key_hash=key_hash,
        key_last_chars=last_chars,
        permissions_json=permissions_json
    )
    
    print("\n📦 SQL para Banco de Dados:")
    print("-" * 50)
    print(sql_content)
    print("-" * 50)
    
    # Append to summary file if needed, or just print key for user
    print(f"\n🔑 Nova API Key ({system_name}): {full_key}")
    print("⚠️  SALVE ESTA CHAVE AGORA! Ela não poderá ser recuperada.")

if __name__ == "__main__":
    main()
