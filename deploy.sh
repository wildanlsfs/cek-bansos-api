#!/bin/bash

# Cek Bansos API - Deployment Script v2
# Supports separate docker-compose files for each provider

set -e

echo "🚀 Cek Bansos API Deployment v2"
echo "================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit .env and configure:"
    echo "   - API_KEY (required)"
    echo "   - AI_PROVIDER (ollama or 9router)"
    echo "   - NINEROUTER_API_KEY (if using 9router)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Load environment
source .env

# Check provider configuration
if [ -z "$AI_PROVIDER" ]; then
    AI_PROVIDER="ollama"
fi

echo "📋 Configuration:"
echo "   AI Provider: $AI_PROVIDER"
echo ""

if [ "$AI_PROVIDER" = "9router" ]; then
    # 9router deployment
    if [ -z "$NINEROUTER_API_KEY" ]; then
        echo "❌ Error: NINEROUTER_API_KEY not set in .env"
        echo "   Get your API key from https://9router.com"
        exit 1
    fi
    
    echo "   9router API Key: ${NINEROUTER_API_KEY:0:10}..."
    echo ""
    echo "☁️  Deploying with 9router cloud API..."
    echo "   Using: docker-compose.9router.yml"
    echo ""
    
    docker compose -f docker-compose.9router.yml up -d
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📡 API Status:"
    echo "   Health: curl http://localhost:8000/health"
    echo "   Docs: http://localhost:8000/docs"
    
elif [ "$AI_PROVIDER" = "ollama" ]; then
    # Ollama deployment
    echo "   Ollama URL: ${OLLAMA_URL:-http://ollama:11434}"
    echo ""
    echo "📦 Deploying with local Ollama..."
    echo "   Using: docker-compose.ollama.yml"
    echo "   This will download the gemma4:e2b model (~7GB)"
    echo "   First run may take 10-15 minutes"
    echo ""
    
    docker compose -f docker-compose.ollama.yml up -d
    
    echo ""
    echo "⏳ Waiting for Ollama to be ready..."
    sleep 5
    
    echo ""
    echo "✅ Deployment started!"
    echo ""
    echo "📥 Model download progress:"
    echo "   docker compose -f docker-compose.ollama.yml logs -f model-downloader"
    echo ""
    echo "📡 API Status (after model download):"
    echo "   Health: curl http://localhost:8000/health"
    echo "   Docs: http://localhost:8000/docs"
    
else
    echo "❌ Error: Unknown AI_PROVIDER: $AI_PROVIDER"
    echo "   Valid options: ollama, 9router"
    exit 1
fi

echo ""
echo "🧪 Test API:"
echo '   curl -X POST http://localhost:8000/check-nik \'
echo '     -H "Authorization: Bearer '$API_KEY'" \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"nik": "1234567890123456"}'"'"
echo ""
echo "📊 View logs:"
if [ "$AI_PROVIDER" = "ollama" ]; then
    echo "   docker compose -f docker-compose.ollama.yml logs -f api"
else
    echo "   docker compose -f docker-compose.9router.yml logs -f api"
fi
echo ""
echo "🎉 Ready to process NIK checks!"
