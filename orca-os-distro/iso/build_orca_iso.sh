#!/bin/bash
set -e

echo "🐋 Building Orca OS Distribution ISO..."

# Configuration
ORCA_VERSION="23.04"
BASE_ISO="ubuntu-22.04.3-desktop-amd64.iso"
ORCA_ISO="OrcaOS-${ORCA_VERSION}-amd64.iso"
BUILD_DIR="orca-os-build"

# Clean previous builds
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Download base ISO if not exists
if [ ! -f "$BASE_ISO" ]; then
    echo "Downloading Ubuntu 22.04 LTS base ISO..."
    wget https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso
fi

# Extract ISO
echo "Extracting base ISO..."
7z x "$BASE_ISO" -o"$BUILD_DIR/extract" -y

# Copy Orca OS core to the ISO
echo "Installing Orca OS core..."
cp -r ../orca-core "$BUILD_DIR/extract/opt/orca-os/"

# Create Orca OS systemd service
cat > "$BUILD_DIR/extract/etc/systemd/system/orca-ai.service" << 'EOF'
[Unit]
Description=Orca AI - Core System AI Service
Documentation=https://orca-os.dev
After=network.target multi-user.target
Wants=network.target

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python -m orca --daemon --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=orca-ai

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/orca /var/log/orca

[Install]
WantedBy=multi-user.target
EOF

# Create orca system user
cat > "$BUILD_DIR/extract/etc/passwd.orca" << 'EOF'
orca:x:1001:1001:Orca AI Service:/var/lib/orca:/bin/false
EOF

# Create orca group
cat > "$BUILD_DIR/extract/etc/group.orca" << 'EOF'
orca:x:1001:
EOF

# Install Orca OS during installation
cat > "$BUILD_DIR/extract/usr/local/bin/install-orca-os.sh" << 'EOF'
#!/bin/bash
set -e

echo "🐋 Installing Orca OS AI Engine..."

# Create orca user
useradd -r -s /bin/false -d /var/lib/orca orca

# Create directories
mkdir -p /var/lib/orca
mkdir -p /var/log/orca
mkdir -p /etc/orca

# Set permissions
chown -R orca:orca /var/lib/orca
chown -R orca:orca /var/log/orca

# Install Python dependencies
cd /opt/orca-os
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download LLaMA 3.1 model
ollama pull llama3.1

# Enable Orca AI service
systemctl daemon-reload
systemctl enable orca-ai.service

# Create desktop entry
cat > /usr/share/applications/orca-ai.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca AI
Comment=AI-Powered System Assistant
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

# Create AI-powered package manager
cat > /usr/local/bin/orca-install << 'PACKAGE_EOF'
#!/bin/bash
# AI-powered package manager
orca "install $*"
PACKAGE_EOF

chmod +x /usr/local/bin/orca-install

echo "✅ Orca OS installed successfully!"
echo "AI service will start automatically on boot"
echo "Use 'orca \"your query\"' to interact with Orca AI"
EOF

chmod +x "$BUILD_DIR/extract/usr/local/bin/install-orca-os.sh"

# Customize boot screen
echo "Customizing boot screen..."
cp ../desktop/boot-splash.png "$BUILD_DIR/extract/isolinux/splash.png" 2>/dev/null || true

# Customize desktop
echo "Customizing desktop environment..."
mkdir -p "$BUILD_DIR/extract/etc/skel/.config/autostart"
cat > "$BUILD_DIR/extract/etc/skel/.config/autostart/orca-ai.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Orca AI
Comment=AI-Powered System Assistant
Exec=/opt/orca-os/venv/bin/python -m orca --overlay
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Create welcome message
cat > "$BUILD_DIR/extract/etc/motd" << 'EOF'
🐋 Welcome to Orca OS - AI-Native Linux Distribution!

Orca AI is now running and ready to help you.

Quick Start:
  orca "show me disk usage"     # Ask Orca anything
  orca "install docker"         # AI-powered package management
  orca --overlay                # Start global overlay (Ctrl+Space)
  systemctl status orca-ai      # Check AI service status

Orca OS - Where AI is the operating system! 🐋
EOF

# Create ISO
echo "Creating Orca OS ISO..."
cd "$BUILD_DIR/extract"
mkisofs -D -r -V "Orca OS ${ORCA_VERSION}" -cache-inodes -J -l \
    -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot \
    -boot-load-size 4 -boot-info-table -o "../${ORCA_ISO}" .

cd ..

echo "✅ Orca OS ISO created successfully!"
echo "ISO: ${ORCA_ISO}"
echo "Size: $(du -h ${ORCA_ISO} | cut -f1)"
echo ""
echo "To test:"
echo "1. Write ISO to USB: sudo dd if=${ORCA_ISO} of=/dev/sdX bs=4M"
echo "2. Boot from USB and install Orca OS"
echo "3. On first boot, Orca AI will be running automatically"
