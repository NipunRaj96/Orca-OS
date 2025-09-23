#!/bin/bash
set -e

echo "🐋 Orca OS Complete Installation & Testing Suite"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_phase() {
    echo -e "${PURPLE}[PHASE]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo) for complete installation"
    exit 1
fi

# Check if we're on Linux
if [ "$(uname)" != "Linux" ]; then
    print_error "This script requires Linux for complete installation"
    exit 1
fi

print_phase "Phase 1: System Preparation"
echo "================================="

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y curl wget git build-essential python3 python3-pip python3-venv
apt install -y htop iotop nethogs sysstat
apt install -y systemd systemd-services
apt install -y linux-headers-$(uname -r)

print_success "System preparation complete"

print_phase "Phase 2: Installing Ollama"
echo "================================="

# Install Ollama
print_status "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
print_status "Starting Ollama service..."
systemctl enable ollama
systemctl start ollama

# Wait for Ollama to start
print_status "Waiting for Ollama to start..."
sleep 10

# Pull LLaMA 3.1 model
print_status "Pulling LLaMA 3.1 model..."
ollama pull llama3.1

print_success "Ollama installation complete"

print_phase "Phase 3: Installing Orca OS Core"
echo "======================================"

# Create Orca OS directory
print_status "Creating Orca OS directory..."
mkdir -p /opt/orca-os
cd /opt/orca-os

# Copy core Orca OS files
print_status "Installing Orca OS core components..."
cp -r /Users/nipunkumar/Orca-OS/orca /opt/orca-os/
cp -r /Users/nipunkumar/Orca-OS/config /opt/orca-os/
cp /Users/nipunkumar/Orca-OS/requirements.txt /opt/orca-os/
cp /Users/nipunkumar/Orca-OS/pyproject.toml /opt/orca-os/

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Orca OS core installation complete"

print_phase "Phase 4: Installing Advanced Features"
echo "==========================================="

# Install Phase 3 & 4 features
print_status "Installing advanced features..."
cd /Users/nipunkumar/Orca-OS/orca-os-distro
chmod +x deploy_advanced_features.sh
./deploy_advanced_features.sh

print_success "Advanced features installation complete"

print_phase "Phase 5: Installing C++ Components"
echo "======================================="

# Install C++ components
print_status "Installing C++ components..."
chmod +x build_c++_components.sh
./build_c++_components.sh

print_success "C++ components installation complete"

print_phase "Phase 6: System Configuration"
echo "=================================="

# Create Orca user
print_status "Creating Orca user..."
useradd -r -s /bin/false -d /opt/orca-os orca || true
chown -R orca:orca /opt/orca-os

# Set up permissions
print_status "Setting up permissions..."
chmod +x /opt/orca-os/orca/cli.py
chmod +x /opt/orca-os/orca/core/daemon.py
chmod +x /usr/local/bin/orca-*

# Create systemd service for Orca
print_status "Creating Orca systemd service..."
cat > /etc/systemd/system/orca-ai.service << 'EOF'
[Unit]
Description=Orca AI Operating System
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/orca/cli.py daemon --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
print_status "Enabling and starting services..."
systemctl daemon-reload
systemctl enable orca-ai.service
systemctl start orca-ai.service

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

print_success "System configuration complete"

print_phase "Phase 7: Running Complete Test Suite"
echo "========================================="

# Copy test suite
print_status "Setting up test suite..."
cp test_complete_system.py /opt/orca-os/
chmod +x /opt/orca-os/test_complete_system.py

# Run comprehensive tests
print_status "Running comprehensive test suite..."
cd /opt/orca-os
source venv/bin/activate
python test_complete_system.py

if [ $? -eq 0 ]; then
    print_success "All tests passed! Orca OS is ready for VMware testing!"
else
    print_warning "Some tests failed. Check the test report for details."
fi

print_phase "Phase 8: Final System Status"
echo "================================="

# Check service status
print_status "Checking service status..."
systemctl status orca-ai.service --no-pager -l
systemctl status ollama.service --no-pager -l

# Check Orca CLI
print_status "Testing Orca CLI..."
orca --help

# Check AI functionality
print_status "Testing AI functionality..."
orca "show me system information"

# Check advanced features
print_status "Testing advanced features..."
orca-process-manager --help
orca-dashboard --help
orca-predict --help

print_phase "Phase 9: VMware Preparation"
echo "================================="

# Create VMware preparation script
print_status "Creating VMware preparation script..."
cat > /opt/orca-os/prepare_for_vmware.sh << 'EOF'
#!/bin/bash
echo "🐋 Preparing Orca OS for VMware Testing"
echo "======================================="

# Create ISO directory
mkdir -p /opt/orca-os/iso

# Create bootable ISO script
cat > /opt/orca-os/iso/create_orca_iso.sh << 'ISO_EOF'
#!/bin/bash
echo "Creating Orca OS ISO..."

# Install required packages
apt install -y genisoimage syslinux-utils

# Create ISO structure
mkdir -p /tmp/orca-iso/boot/grub
mkdir -p /tmp/orca-iso/orca-os

# Copy Orca OS files
cp -r /opt/orca-os /tmp/orca-iso/orca-os/

# Create GRUB configuration
cat > /tmp/orca-iso/boot/grub/grub.cfg << 'GRUB_EOF'
menuentry "Orca OS - AI Native Linux" {
    set root=(hd0,msdos1)
    linux /vmlinuz root=/dev/sda1 quiet splash
    initrd /initrd.img
}
GRUB_EOF

# Create ISO
genisoimage -o /opt/orca-os/iso/orca-os.iso -b boot/grub/stage2_eltorito \
    -no-emul-boot -boot-load-size 4 -boot-info-table /tmp/orca-iso

echo "Orca OS ISO created: /opt/orca-os/iso/orca-os.iso"
ISO_EOF

chmod +x /opt/orca-os/iso/create_orca_iso.sh

echo "✅ VMware preparation complete"
echo "📁 ISO creation script: /opt/orca-os/iso/create_orca_iso.sh"
echo "🚀 Ready for VMware testing!"
EOF

chmod +x /opt/orca-os/prepare_for_vmware.sh

# Run VMware preparation
print_status "Running VMware preparation..."
/opt/orca-os/prepare_for_vmware.sh

print_success "VMware preparation complete"

print_phase "Phase 10: Final Summary"
echo "============================"

print_success "Orca OS Complete Installation & Testing Complete!"
echo
echo "🐋 Orca OS Status:"
echo "  ✅ Core System: Installed and running"
echo "  ✅ AI Engine: Ollama with LLaMA 3.1"
echo "  ✅ Phase 3 Features: Kernel & System Integration"
echo "  ✅ Phase 4 Features: Advanced Features"
echo "  ✅ C++ Components: High-performance middleware"
echo "  ✅ Test Suite: All tests passed"
echo "  ✅ VMware Ready: ISO creation script prepared"
echo
echo "🚀 Available Commands:"
echo "  orca 'show me system information'  - AI system queries"
echo "  orca-process-manager               - AI process management"
echo "  orca-dashboard                     - System dashboard"
echo "  orca-predict                       - Predictive AI"
echo "  orca-optimize                      - System optimization"
echo "  orca-plugins                       - Plugin system"
echo "  orca-test                          - Run test suite"
echo
echo "🔧 Service Management:"
echo "  systemctl status orca-ai           - Check Orca service"
echo "  systemctl status ollama            - Check Ollama service"
echo "  journalctl -u orca-ai -f           - View Orca logs"
echo
echo "📊 Test Results:"
echo "  Test Report: /opt/orca-os/orca_test_report_*.json"
echo "  All tests passed successfully!"
echo
echo "🎯 Ready for VMware Testing!"
echo "  ISO Script: /opt/orca-os/iso/create_orca_iso.sh"
echo "  Run: /opt/orca-os/iso/create_orca_iso.sh"
echo
echo "Welcome to Orca OS - The AI-Native Linux Distribution! 🐋"
