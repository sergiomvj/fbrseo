# SEO API Python SDK

Cliente Python oficial para integração com a SEO API.

## Instalação

```bash
pip install seo-api-client
# ou
pip install -e ./sdk/python
```

## Uso Rápido

```python
from seo_api import SEOClient

# Inicializar
client = SEOClient(
    base_url="http://localhost:8000",
    api_key="sk_live_xxxxx"
)

# Criar domínio
domain = client.domains.create(
    url="https://meusite.com",
    name="Meu Site"
)

# Listar keywords
keywords = client.keywords.list(domain_id=domain["id"])

# Importar CSV
result = client.imports.semrush_keywords(
    domain_id=1,
    file_path="keywords.csv"
)
```

## Módulos Disponíveis

- `client.domains` - Gerenciamento de domínios
- `client.keywords` - Keywords e rankings
- `client.imports` - Import de dados CSV
- `client.auth` - Informações da API Key
