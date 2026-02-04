# SEO API - Dashboard Frontend

Dashboard administrativo em React para gerenciar a API de SEO.

## Funcionalidades

- 📊 Dashboard com métricas principais
- 👥 Gerenciamento de clientes
- 🔑 Gerenciamento de API Keys
- 🌐 Gerenciamento de domínios
- 📁 Upload de CSVs do SemRush
- 📈 Visualização de rankings e keywords
- 📊 Gráficos e relatórios
- 📋 Logs de uso da API

## Desenvolvimento

```bash
npm install
npm start
```

Acesse: http://localhost:3000

## Build para Produção

```bash
npm run build
```

## Estrutura

```
src/
├── components/     # Componentes reutilizáveis
├── pages/          # Páginas da aplicação
├── services/       # Cliente da API
├── utils/          # Utilitários
└── App.js          # Componente principal
```

## Variáveis de Ambiente

Crie `.env.local`:

```
REACT_APP_API_URL=http://localhost:8000
```
