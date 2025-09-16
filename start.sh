#!/bin/bash

echo "🏥 Starting MedAgg Healthcare POC..."
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   You can use the default values for local development."
    read -p "Press Enter to continue after editing .env file..."
fi

echo "🐳 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service health..."
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Admin Dashboard: http://localhost:3000/admin"

echo ""
echo "✅ MedAgg Healthcare POC is starting up!"
echo ""
echo "📋 Next steps:"
echo "1. Wait for all services to be ready (about 2-3 minutes)"
echo "2. Visit http://localhost:3000 to access the application"
echo "3. Use the admin dashboard at http://localhost:3000/admin"
echo "4. Submit a patient form to test the AI call system"
echo ""
echo "🔧 To stop the services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f"
echo ""
echo "Happy coding! 🚀"


