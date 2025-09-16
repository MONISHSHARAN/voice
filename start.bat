@echo off
echo 🏥 Starting MedAgg Healthcare POC...
echo ==================================

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration before continuing.
    echo    You can use the default values for local development.
    pause
)

echo 🐳 Starting Docker services...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak > nul

echo 🔍 Checking service health...
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo Admin Dashboard: http://localhost:3000/admin

echo.
echo ✅ MedAgg Healthcare POC is starting up!
echo.
echo 📋 Next steps:
echo 1. Wait for all services to be ready (about 2-3 minutes)
echo 2. Visit http://localhost:3000 to access the application
echo 3. Use the admin dashboard at http://localhost:3000/admin
echo 4. Submit a patient form to test the AI call system
echo.
echo 🔧 To stop the services: docker-compose down
echo 📊 To view logs: docker-compose logs -f
echo.
echo Happy coding! 🚀
pause


