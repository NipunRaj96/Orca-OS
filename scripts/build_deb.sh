#!/bin/bash
set -e

echo "🐋 Building Orca OS .deb package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/ debian/orca-os/

# Install build dependencies
echo "Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y devscripts debhelper python3-all python3-setuptools

# Make scripts executable
chmod +x debian/postinst
chmod +x debian/prerm
chmod +x debian/rules

# Build the package
echo "Building .deb package..."
dpkg-buildpackage -us -uc -b

echo "✅ .deb package built successfully!"
echo "Package: orca-os_0.1.0_all.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i orca-os_0.1.0_all.deb"
echo "  sudo apt-get install -f  # Fix any dependencies"
echo ""
echo "To test:"
echo "  curl -X POST http://localhost:8080/query -H 'Content-Type: application/json' -d '{\"query\":\"show me disk usage\"}'"
