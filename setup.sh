#!/bin/bash

echo "🚀 SEO API - Setup Rápido"
echo "=========================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Por favor instale o Docker primeiro.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado. Por favor instale o Docker Compose primeiro.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker e Docker Compose encontrados${NC}"
echo ""

# Copia .env se não existir
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}📝 Criando arquivo .env...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✅ Arquivo .env criado. Edite backend/.env conforme necessário.${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi
echo ""

# Pergunta se quer iniciar os serviços
read -p "Deseja iniciar os serviços agora? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🐳 Iniciando containers...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    
    echo ""
    echo -e "${GREEN}✅ Serviços iniciados!${NC}"
    echo ""
    echo "📍 URLs:"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Frontend: http://localhost:3000"
    echo ""
    echo "🔍 Verificar logs:"
    echo "   docker-compose -f docker-compose.dev.yml logs -f backend"
    echo ""
    echo "🛑 Parar serviços:"
    echo "   docker-compose -f docker-compose.dev.yml down"
    echo ""
    
    # Espera serviços iniciarem
    echo -e "${YELLOW}⏳ Aguardando serviços iniciarem (30s)...${NC}"
    sleep 30
    
    # Cria um cliente de exemplo
    echo -e "${YELLOW}👤 Criando cliente de exemplo...${NC}"
    curl -s -X POST "http://localhost:8000/api/v1/auth/clients" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Cliente Exemplo",
        "company": "Empresa Exemplo",
        "email": "exemplo@empresa.com",
        "rate_limit_per_minute": 60,
        "rate_limit_per_day": 10000
      }' | python3 -m json.tool
    
    echo ""
    echo -e "${GREEN}✅ Setup completo!${NC}"
    echo ""
    echo "📚 Próximos passos:"
    echo "   1. Acesse http://localhost:8000/docs"
    echo "   2. Crie uma API Key em /api/v1/auth/clients/1/api-keys"
    echo "   3. Use a API Key para fazer chamadas"
    echo ""
else
    echo -e "${YELLOW}ℹ️  Setup cancelado. Para iniciar manualmente:${NC}"
    echo "   docker-compose -f docker-compose.dev.yml up -d"
fi
