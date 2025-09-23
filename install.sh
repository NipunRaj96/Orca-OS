#!/bin/bash

# Orca OS Installation Script
# Installs the AI-powered operating system interface

set -e

echo "🐋 Installing Orca OS - AI-Powered Operating System"
echo "=================================================="

# Get current directory
ORCA_DIR=$(pwd)
echo "📁 Installing from: $ORCA_DIR"

# Create virtual environment
echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_macos.txt

# Create global command
echo "🔧 Creating global command..."
sudo ln -sf "$ORCA_DIR/orca_os.py" /usr/local/bin/orca-os
sudo chmod +x /usr/local/bin/orca-os

# Create desktop shortcut
echo "🖥️  Creating desktop integration..."
mkdir -p ~/Applications
cat > ~/Applications/Orca\ OS.app/Contents/MacOS/orca-os << EOF
#!/bin/bash
cd "$ORCA_DIR"
source venv/bin/activate
python orca_os.py
EOF

chmod +x ~/Applications/Orca\ OS.app/Contents/MacOS/orca-os

# Create configuration
echo "⚙️  Setting up configuration..."
mkdir -p ~/.orca
cp config/orca.yaml ~/.orca/

echo ""
echo "🎉 Orca OS installation complete!"
echo ""
echo "🚀 How to use:"
echo "  • Interactive mode: orca-os"
echo "  • Single command: orca-os 'show me disk usage'"
echo "  • Desktop app: Open 'Orca OS' from Applications"
echo ""
echo "💡 Examples:"
echo "  orca-os 'find large files on my computer'"
echo "  orca-os 'check if my computer is running slowly'"
echo "  orca-os 'show me what programs are running'"
echo ""
echo "🐋 Welcome to Orca OS - Your AI Operating System!"
