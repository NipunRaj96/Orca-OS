#!/bin/bash

# Orca OS Installation Script

set -e

echo "🐋 Installing Orca OS..."

# Check if Python 3.9+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.9+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Orca in development mode
echo "🔧 Installing Orca OS..."
pip install -e .

# Create data directory
echo "📁 Creating data directory..."
mkdir -p ~/.orca

# Copy default configuration
echo "⚙️  Setting up configuration..."
cp config/orca.yaml ~/.orca/orca.yaml

# Check for Ollama
echo "🤖 Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing Ollama..."
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Start Ollama service
    ollama serve &
    sleep 5
    
    # Pull the default model
    echo "📥 Downloading LLaMA 2 7B model (this may take a while)..."
    ollama pull llama2:7b
else
    echo "✅ Ollama found"
fi

# Create systemd service (optional)
echo "🔧 Setting up systemd service..."
cat > /tmp/orca-daemon.service << EOF
[Unit]
Description=Orca OS Daemon
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python -m orca daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📋 Systemd service created at /tmp/orca-daemon.service"
echo "   To install: sudo cp /tmp/orca-daemon.service /etc/systemd/system/"
echo "   To enable: sudo systemctl enable orca-daemon"
echo "   To start: sudo systemctl start orca-daemon"

echo ""
echo "🎉 Orca OS installation complete!"
echo ""
echo "Quick start:"
echo "  source venv/bin/activate"
echo "  orca 'show me disk usage'"
echo ""
echo "To start the daemon:"
echo "  orca daemon"
echo ""
echo "For more information, see README.md"
