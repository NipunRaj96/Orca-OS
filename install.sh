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
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python3 -m orca.database.init_db

# Create global command wrapper
echo "🔧 Creating global command..."
cat > /tmp/orca-wrapper.sh << EOF
#!/bin/bash
cd "$ORCA_DIR"
source venv/bin/activate
python3 -m orca.cli "\$@"
EOF

sudo mv /tmp/orca-wrapper.sh /usr/local/bin/orca
sudo chmod +x /usr/local/bin/orca

# Create configuration
echo "⚙️  Setting up configuration..."
mkdir -p ~/.orca
if [ ! -f ~/.orca/orca.yaml ]; then
    cp config/orca.yaml ~/.orca/ 2>/dev/null || echo "⚠️  Config file not found, using defaults"
fi

echo ""
echo "🎉 Orca OS installation complete!"
echo ""
echo "🚀 How to use:"
echo "  • Interactive mode: orca --interactive"
echo "  • Single command: orca 'show me disk usage'"
echo "  • Health check: orca 'show health score'"
echo "  • Organize files: orca 'organize my downloads'"
echo ""
echo "💡 Examples:"
echo "  orca 'show me disk usage'"
echo "  orca 'show health score'"
echo "  orca 'organize my downloads'"
echo "  orca 'show my usage patterns'"
echo "  orca 'optimize my system'"
echo ""
echo "📚 Documentation: See docs/QUICK_START_GUIDE.md"
echo ""
echo "🐋 Welcome to Orca OS - Your AI Operating System!"
