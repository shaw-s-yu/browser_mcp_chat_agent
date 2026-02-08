#!/bin/bash
# Quick Setup Script for Oracle Docker Configuration

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Browser Automation + Oracle Docker Setup                  ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Step 1: Check if .env exists
echo ""
echo "📋 Step 1: Setting up environment variables..."
if [ -f .env ]; then
    echo "  ✓ .env file already exists"
else
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "  ✓ Created .env from template"
        echo ""
        echo "  ⚠️  IMPORTANT: Edit .env with your Oracle credentials:"
        echo "     - ORACLE_HOST: Your Oracle server IP address"
        echo "     - ORACLE_PORT: Usually 1521"
        echo "     - ORACLE_SERVICE: Your database service name"
        echo "     - ORACLE_USER: Your database username"
        echo "     - ORACLE_PASSWORD: Your database password"
        echo "     - GEMINI_API_KEY: Your Google Gemini API key"
        echo ""
        read -p "  Press Enter after editing .env file..."
    else
        echo "  ✗ .env.example not found!"
        exit 1
    fi
fi

# Step 2: Build Docker image
echo ""
echo "🐳 Step 2: Building Docker image..."
echo "  (This may take several minutes as it downloads Oracle Instant Client)"
if docker-compose build; then
    echo "  ✓ Docker image built successfully"
else
    echo "  ✗ Failed to build Docker image"
    exit 1
fi

# Step 3: Start container
echo ""
echo "🚀 Step 3: Starting Docker container..."
if docker-compose up -d; then
    echo "  ✓ Container started successfully"
else
    echo "  ✗ Failed to start container"
    exit 1
fi

# Step 4: Wait for container to be ready
echo ""
echo "⏳ Step 4: Waiting for container to be ready..."
sleep 5

# Step 5: Test Oracle connection
echo ""
echo "🔗 Step 5: Testing Oracle database connection..."
if docker exec -it ubuntu-novnc python /home/user/app/test_oracle_connection.py; then
    echo "  ✓ Oracle connection test passed!"
else
    echo "  ⚠️  Oracle connection test failed"
    echo "  Please check your .env configuration"
fi

# Step 6: Display access information
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✨ Setup Complete!                                         ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Access the application at:                                ║"
echo "║  🌐 http://localhost:5000                                  ║"
echo "║                                                            ║"
echo "║  Container name: ubuntu-novnc                             ║"
echo "║  Run commands inside container:                           ║"
echo "║  $ docker exec -it ubuntu-novnc bash                      ║"
echo "║                                                            ║"
echo "║  View logs:                                                ║"
echo "║  $ docker-compose logs -f ubuntu-novnc                    ║"
echo "║                                                            ║"
echo "║  Stop the container:                                       ║"
echo "║  $ docker-compose down                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
