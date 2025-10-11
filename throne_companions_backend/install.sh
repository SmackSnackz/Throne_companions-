#!/bin/bash

# Throne Companions Backend Installation Script

set -e  # Exit on any error

echo "==================================="
echo "Throne Companions Backend Installer"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "✓ Python $python_version detected (>= 3.11 required)"
else
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✓ pip3 is available"

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

# Install emergentintegrations first with the custom index
echo "Installing emergentintegrations..."
pip3 install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ emergentintegrations==0.1.0

# Install other dependencies
echo "Installing other dependencies..."
pip3 install -r requirements.txt

echo "✓ All dependencies installed successfully!"

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your configuration."
    echo ""
    echo "⚠ IMPORTANT: Edit the .env file with your actual configuration:"
    echo "  - EMERGENT_LLM_KEY (required for AI functionality)"
    echo "  - MONGO_URL (MongoDB connection string)"
    echo "  - JWT_SECRET (for authentication)"
    echo "  - ADMIN_EMAILS (admin email addresses)"
else
    echo "✓ .env file already exists"
fi

# Make start script executable
chmod +x start.sh

echo ""
echo "==================================="
echo "Installation completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration"
echo "2. Ensure MongoDB is running"
echo "3. Run: ./start.sh"
echo ""
echo "The API will be available at: http://localhost:8001"
echo "API documentation: http://localhost:8001/docs"
echo ""
