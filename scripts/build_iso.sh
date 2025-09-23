#!/bin/bash
set -e

echo "🐋 Building Orca OS ISO with Cubic..."

# Check if Cubic is installed
if ! command -v cubic &> /dev/null; then
    echo "Installing Cubic..."
    sudo apt-get update
    sudo apt-get install -y cubic
fi

# Create ISO build directory
BUILD_DIR="orca-os-iso"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "Setting up Orca OS ISO build..."

# Download Ubuntu 22.04 LTS ISO
if [ ! -f "ubuntu-22.04.3-desktop-amd64.iso" ]; then
    echo "Downloading Ubuntu 22.04 LTS ISO..."
    wget https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso
fi

# Create Cubic project
echo "Creating Cubic project..."
cubic --create-project "$BUILD_DIR" ubuntu-22.04.3-desktop-amd64.iso

# Copy Orca OS files to the project
echo "Copying Orca OS files..."
cp -r . "$BUILD_DIR/extract-cubic/opt/orca-os/"
cd "$BUILD_DIR/extract-cubic/opt/orca-os/"

# Create installation script
cat > install_orca.sh << 'EOF'
#!/bin/bash
set -e

echo "🐋 Installing Orca OS..."

# Install dependencies
apt-get update
apt-get install -y python3 python3-pip python3-venv python3-dev build-essential curl

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download LLaMA 3.1 model
ollama pull llama3.1

# Install Orca OS
cd /opt/orca-os
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/orca-os.service << 'SERVICE_EOF'
[Unit]
Description=Orca OS - AI-Powered Linux Assistant
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python -m orca --daemon --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Enable service
systemctl daemon-reload
systemctl enable orca-os.service

# Create desktop entry
cat > /usr/share/applications/orca-os.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca OS
Comment=AI-Powered Linux Assistant
Exec=/opt/orca-os/venv/bin/python -m orca --overlay
Icon=orca
Terminal=false
Categories=System;Utility;
DESKTOP_EOF

# Create launcher script
cat > /usr/local/bin/orca << 'LAUNCHER_EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python -m orca "$@"
LAUNCHER_EOF

chmod +x /usr/local/bin/orca

echo "✅ Orca OS installed successfully!"
echo "Service will start automatically on boot"
echo "Use 'orca \"your query\"' to interact with Orca OS"
EOF

chmod +x install_orca.sh

# Create desktop customization
mkdir -p "$BUILD_DIR/extract-cubic/etc/skel/.config/autostart"
cat > "$BUILD_DIR/extract-cubic/etc/skel/.config/autostart/orca-os.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Orca OS
Comment=AI-Powered Linux Assistant
Exec=/opt/orca-os/venv/bin/python -m orca --overlay
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Create welcome message
cat > "$BUILD_DIR/extract-cubic/etc/motd" << 'EOF'
🐋 Welcome to Orca OS - AI-Powered Linux!

Orca OS is now installed and ready to use.

Quick Start:
  orca "show me disk usage"     # Ask Orca anything
  orca --overlay                # Start global overlay (Ctrl+Space)
  systemctl status orca-os      # Check service status

Documentation: https://docs.orca-os.dev
Support: https://github.com/orca-os/orca-os

Enjoy your AI-powered Linux experience! 🐋
EOF

# Create boot customization
cat > "$BUILD_DIR/extract-cubic/usr/share/plymouth/themes/ubuntu-logo/ubuntu-logo.script" << 'EOF'
# Add Orca OS branding to boot screen
if [ -f /etc/orca-os-version ]; then
    echo "🐋 Orca OS - AI-Powered Linux"
fi
EOF

echo "✅ Orca OS ISO build setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: cubic $BUILD_DIR"
echo "2. In Cubic, run: /opt/orca-os/install_orca.sh"
echo "3. Customize desktop and boot screen"
echo "4. Generate ISO"
echo ""
echo "The ISO will be created as: $BUILD_DIR/orca-os-22.04.3-desktop-amd64.iso"
