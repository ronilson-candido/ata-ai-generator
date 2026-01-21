@echo off
echo 🚀 Iniciando Cyber Lab - Meeting Minutes AI...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando. Por favor, inicie o Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker está rodando
echo.

REM Stop existing containers
echo 🛑 Parando containers existentes...
docker-compose down

REM Build and start
echo 🔨 Construindo e iniciando serviços...
docker-compose up -d --build

echo.
echo ⏳ Aguardando serviços iniciarem...
timeout /t 10 /nobreak >nul

REM Check services
echo.
echo 📊 Status dos serviços:
docker-compose ps

echo.
echo ✨ Aplicação iniciada com sucesso!
echo.
echo 🌐 Acesse:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📝 Para ver logs:
echo    docker-compose logs -f
echo.
echo 🛑 Para parar:
echo    docker-compose down
echo.
pause
