#!/bin/bash

# Biomedical Research Platform Startup Script

echo "🧬 Starting Agentic AI-Enabled Biomedical Research Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
# Environment variables for the Biomedical Research Platform
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./data/biomedical_platform.db
PYTHONPATH=/app
LOG_LEVEL=INFO
EOF
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
    read -p "Press Enter to continue after updating .env file..."
fi

# Create data directory
mkdir -p data logs

# Build and start services
echo "🚀 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend service is running at http://localhost:8000"
else
    echo "❌ Backend service is not responding"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service is running at http://localhost:3000"
else
    echo "❌ Frontend service is not responding"
fi

echo ""
echo "🎉 Platform is ready!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the platform, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"

