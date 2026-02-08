@echo off
REM Quick Setup Script for Oracle Docker Configuration (Windows)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Browser Automation + Oracle Docker Setup (Windows)        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check if .env exists
echo 📋 Step 1: Setting up environment variables...
if exist .env (
    echo   ✓ .env file already exists
) else (
    if exist .env.example (
        copy .env.example .env
        echo   ✓ Created .env from template
        echo.
        echo   ⚠️  IMPORTANT: Edit .env with your Oracle credentials:
        echo      - ORACLE_HOST: Your Oracle server IP address
        echo      - ORACLE_PORT: Usually 1521
        echo      - ORACLE_SERVICE: Your database service name
        echo      - ORACLE_USER: Your database username
        echo      - ORACLE_PASSWORD: Your database password
        echo      - GEMINI_API_KEY: Your Google Gemini API key
        echo.
        pause
    ) else (
        echo   ✗ .env.example not found!
        pause
        exit /b 1
    )
)

REM Step 2: Check Docker
echo.
echo 🐳 Step 2: Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ Docker is not installed or not in PATH!
    echo   Please install Docker Desktop for Windows
    pause
    exit /b 1
) else (
    echo   ✓ Docker is installed
)

REM Step 3: Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ Docker Compose is not installed!
    pause
    exit /b 1
) else (
    echo   ✓ Docker Compose is installed
)

REM Step 4: Build Docker image
echo.
echo 🚀 Step 3: Building Docker image...
echo   (This may take several minutes as it downloads Oracle Instant Client)
docker-compose build
if errorlevel 1 (
    echo   ✗ Failed to build Docker image
    pause
    exit /b 1
) else (
    echo   ✓ Docker image built successfully
)

REM Step 5: Start container
echo.
echo 🚀 Step 4: Starting Docker container...
docker-compose up -d
if errorlevel 1 (
    echo   ✗ Failed to start container
    pause
    exit /b 1
) else (
    echo   ✓ Container started successfully
)

REM Step 6: Wait for container to be ready
echo.
echo ⏳ Step 5: Waiting for container to be ready...
timeout /t 5 /nobreak

REM Step 7: Display access information
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  ✨ Setup Complete!                                         ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  Access the application at:                                ║
echo ║  🌐 http://localhost:5000                                  ║
echo ║                                                            ║
echo ║  Container name: ubuntu-novnc                             ║
echo ║                                                            ║
echo ║  Useful commands:                                          ║
echo ║  - View logs:    docker-compose logs -f ubuntu-novnc      ║
echo ║  - Stop container: docker-compose down                    ║
echo ║  - Enter container: docker exec -it ubuntu-novnc bash     ║
echo ║                                                            ║
echo ║  Test Oracle connection (inside container):               ║
echo ║  $ python /home/user/app/test_oracle_connection.py       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
