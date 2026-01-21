#!/bin/bash

echo "🚀 Iniciando Cyber Lab - Meeting Minutes AI..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker Desktop."
    exit 1
fi

echo "✅ Docker está rodando"

# Stop existing containers
echo "🛑 Parando containers existentes..."
docker-compose down

# Build and start
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

echo ""
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Check services
echo ""
echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "✨ Aplicação iniciada com sucesso!"
echo ""
echo "🌐 Acesse:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Para ver logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar:"
echo "   docker-compose down"
