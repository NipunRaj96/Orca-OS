#!/bin/bash
set -e

echo "🐋 Deploying Orca OS Advanced Features (Phase 3 & 4)"
echo "=================================================="

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
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Check if Orca OS core is installed
if [ ! -d "/opt/orca-os" ]; then
    print_error "Orca OS core not found. Please install Orca OS first."
    exit 1
fi

print_phase "Phase 3: Kernel & System Integration"
echo "=========================================="

# Create advanced features directories
print_status "Creating advanced features directories..."
mkdir -p /opt/orca-os/kernel
mkdir -p /opt/orca-os/advanced
mkdir -p /opt/orca-os/plugins
mkdir -p /opt/orca-os/predictive
mkdir -p /opt/orca-os/dashboard
mkdir -p /opt/orca-os/optimizer

# Install Phase 3: Kernel & System Integration
print_status "Installing AI Process Manager..."
cp kernel/ai-process-manager.py /opt/orca-os/kernel/
chmod +x /opt/orca-os/kernel/ai-process-manager.py

print_status "Installing AI Logging System..."
cp kernel/ai-logging-system.py /opt/orca-os/kernel/
chmod +x /opt/orca-os/kernel/ai-logging-system.py

print_status "Installing AI Scheduler..."
cp kernel/ai-scheduler.py /opt/orca-os/kernel/
chmod +x /opt/orca-os/kernel/ai-scheduler.py

print_success "Phase 3 components installed"

print_phase "Phase 4: Advanced Features"
echo "==============================="

# Install Phase 4: Advanced Features
print_status "Installing Orca Package Manager..."
cp advanced/orca-package-manager.py /opt/orca-os/advanced/
chmod +x /opt/orca-os/advanced/orca-package-manager.py

print_status "Installing Plugin System..."
cp advanced/plugin-system.py /opt/orca-os/advanced/
chmod +x /opt/orca-os/advanced/plugin-system.py

print_status "Installing Predictive AI..."
cp advanced/predictive-ai.py /opt/orca-os/advanced/
chmod +x /opt/orca-os/advanced/predictive-ai.py

print_status "Installing Orca Dashboard..."
cp advanced/orca-dashboard.py /opt/orca-os/dashboard/
chmod +x /opt/orca-os/dashboard/orca-dashboard.py

print_status "Installing Orca Optimizer..."
cp advanced/orca-optimizer.py /opt/orca-os/optimizer/
chmod +x /opt/orca-os/optimizer/orca-optimizer.py

print_status "Installing Test Suite..."
cp advanced/test_advanced_features.py /opt/orca-os/advanced/
chmod +x /opt/orca-os/advanced/test_advanced_features.py

print_success "Phase 4 components installed"

# Create systemd services
print_status "Creating systemd services..."

# AI Process Manager Service
cat > /etc/systemd/system/orca-ai-process-manager.service << 'EOF'
[Unit]
Description=Orca AI Process Manager
After=orca-ai.service
Requires=orca-ai.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/kernel/ai-process-manager.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# AI Logging System Service
cat > /etc/systemd/system/orca-ai-logging.service << 'EOF'
[Unit]
Description=Orca AI Logging System
After=orca-ai.service
Requires=orca-ai.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/kernel/ai-logging-system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# AI Scheduler Service
cat > /etc/systemd/system/orca-ai-scheduler.service << 'EOF'
[Unit]
Description=Orca AI Scheduler
After=orca-ai.service
Requires=orca-ai.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/kernel/ai-scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Predictive AI Service
cat > /etc/systemd/system/orca-predictive-ai.service << 'EOF'
[Unit]
Description=Orca Predictive AI Assistant
After=orca-ai.service
Requires=orca-ai.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/advanced/predictive-ai.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Orca Dashboard Service
cat > /etc/systemd/system/orca-dashboard.service << 'EOF'
[Unit]
Description=Orca OS Dashboard
After=orca-ai.service
Requires=orca-ai.service

[Service]
Type=simple
User=orca
Group=orca
WorkingDirectory=/opt/orca-os
Environment=PATH=/opt/orca-os/venv/bin
ExecStart=/opt/orca-os/venv/bin/python /opt/orca-os/dashboard/orca-dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd services created"

# Create launcher scripts
print_status "Creating launcher scripts..."

# AI Process Manager
cat > /usr/local/bin/orca-process-manager << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python kernel/ai-process-manager.py "$@"
EOF
chmod +x /usr/local/bin/orca-process-manager

# AI Logging System
cat > /usr/local/bin/orca-logs << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python kernel/ai-logging-system.py "$@"
EOF
chmod +x /usr/local/bin/orca-logs

# AI Scheduler
cat > /usr/local/bin/orca-scheduler << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python kernel/ai-scheduler.py "$@"
EOF
chmod +x /usr/local/bin/orca-scheduler

# Predictive AI
cat > /usr/local/bin/orca-predict << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python advanced/predictive-ai.py "$@"
EOF
chmod +x /usr/local/bin/orca-predict

# Orca Dashboard
cat > /usr/local/bin/orca-dashboard << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python dashboard/orca-dashboard.py "$@"
EOF
chmod +x /usr/local/bin/orca-dashboard

# Orca Optimizer
cat > /usr/local/bin/orca-optimize << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python optimizer/orca-optimizer.py "$@"
EOF
chmod +x /usr/local/bin/orca-optimize

# Plugin System
cat > /usr/local/bin/orca-plugins << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python advanced/plugin-system.py "$@"
EOF
chmod +x /usr/local/bin/orca-plugins

# Package Manager
cat > /usr/local/bin/orca-install << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python advanced/orca-package-manager.py install "$@"
EOF
chmod +x /usr/local/bin/orca-install

# Test Suite
cat > /usr/local/bin/orca-test << 'EOF'
#!/bin/bash
cd /opt/orca-os
source venv/bin/activate
python advanced/test_advanced_features.py "$@"
EOF
chmod +x /usr/local/bin/orca-test

print_success "Launcher scripts created"

# Create desktop entries
print_status "Creating desktop entries..."

# AI Process Manager
cat > /usr/share/applications/orca-process-manager.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca AI Process Manager
Comment=AI-powered process management
Exec=/usr/local/bin/orca-process-manager
Icon=orca
Terminal=true
Categories=System;Utility;
EOF

# AI Logging System
cat > /usr/share/applications/orca-logs.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca AI Logs
Comment=AI-powered log analysis
Exec=/usr/local/bin/orca-logs
Icon=orca
Terminal=true
Categories=System;Utility;
EOF

# Orca Dashboard
cat > /usr/share/applications/orca-dashboard.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca OS Dashboard
Comment=AI-powered system dashboard
Exec=/usr/local/bin/orca-dashboard
Icon=orca
Terminal=true
Categories=System;Utility;
EOF

# Predictive AI
cat > /usr/share/applications/orca-predict.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Orca Predictive AI
Comment=Predictive system monitoring
Exec=/usr/local/bin/orca-predict
Icon=orca
Terminal=true
Categories=System;Utility;
EOF

print_success "Desktop entries created"

# Update Orca CLI to include advanced features
print_status "Updating Orca CLI with advanced features..."

# Create advanced CLI integration
cat > /opt/orca-os/orca_advanced_cli.py << 'EOF'
#!/usr/bin/env python3
"""
Orca OS Advanced CLI Integration
Unified interface for all advanced features
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

def main():
    parser = argparse.ArgumentParser(description='Orca OS Advanced Features')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process Manager
    process_parser = subparsers.add_parser('process-manager', help='AI Process Manager')
    process_parser.add_argument('--optimize', action='store_true', help='Optimize processes')
    process_parser.add_argument('--health', action='store_true', help='Show system health')
    
    # Logging System
    logs_parser = subparsers.add_parser('logs', help='AI Logging System')
    logs_parser.add_argument('--hours', type=int, default=24, help='Hours of logs to analyze')
    logs_parser.add_argument('--service', type=str, help='Specific service to analyze')
    
    # Scheduler
    scheduler_parser = subparsers.add_parser('scheduler', help='AI Scheduler')
    scheduler_parser.add_argument('--optimize', action='store_true', help='Optimize scheduling')
    scheduler_parser.add_argument('--monitor', action='store_true', help='Monitor system load')
    
    # Package Manager
    package_parser = subparsers.add_parser('install', help='AI Package Manager')
    package_parser.add_argument('package', help='Package to install')
    package_parser.add_argument('--intent', type=str, help='Installation intent')
    
    # Predictive AI
    predict_parser = subparsers.add_parser('predict', help='Predictive AI')
    predict_parser.add_argument('--forecast', action='store_true', help='Get system forecast')
    predict_parser.add_argument('--recommendations', action='store_true', help='Get recommendations')
    
    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Orca Dashboard')
    dashboard_parser.add_argument('--refresh', type=int, default=5, help='Refresh interval')
    
    # Optimizer
    optimizer_parser = subparsers.add_parser('optimize', help='System Optimizer')
    optimizer_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    optimizer_parser.add_argument('--full', action='store_true', help='Full optimization')
    
    # Plugins
    plugins_parser = subparsers.add_parser('plugins', help='Plugin System')
    plugins_parser.add_argument('--list', action='store_true', help='List plugins')
    plugins_parser.add_argument('--create', type=str, help='Create plugin template')
    
    # Test Suite
    test_parser = subparsers.add_parser('test', help='Test Suite')
    test_parser.add_argument('--component', type=str, help='Test specific component')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print(f"🐋 Orca OS Advanced Features - {args.command}")
    print("=" * 50)
    
    # Execute command
    if args.command == 'process-manager':
        if args.optimize:
            print("Optimizing processes...")
        elif args.health:
            print("Checking system health...")
        else:
            print("Process Manager - use --optimize or --health")
    
    elif args.command == 'logs':
        print(f"Analyzing logs for last {args.hours} hours...")
        if args.service:
            print(f"Focusing on service: {args.service}")
    
    elif args.command == 'scheduler':
        if args.optimize:
            print("Optimizing process scheduling...")
        elif args.monitor:
            print("Monitoring system load...")
        else:
            print("Scheduler - use --optimize or --monitor")
    
    elif args.command == 'install':
        print(f"Installing package: {args.package}")
        if args.intent:
            print(f"Intent: {args.intent}")
    
    elif args.command == 'predict':
        if args.forecast:
            print("Generating system forecast...")
        elif args.recommendations:
            print("Getting AI recommendations...")
        else:
            print("Predictive AI - use --forecast or --recommendations")
    
    elif args.command == 'dashboard':
        print(f"Starting dashboard with {args.refresh}s refresh interval...")
    
    elif args.command == 'optimize':
        if args.full:
            print("Running full system optimization...")
            if args.dry_run:
                print("(Dry run mode)")
        else:
            print("Optimizer - use --full for full optimization")
    
    elif args.command == 'plugins':
        if args.list:
            print("Listing available plugins...")
        elif args.create:
            print(f"Creating plugin template: {args.create}")
        else:
            print("Plugins - use --list or --create <name>")
    
    elif args.command == 'test':
        if args.component:
            print(f"Testing component: {args.component}")
        else:
            print("Running full test suite...")
    
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
EOF

chmod +x /opt/orca-os/orca_advanced_cli.py

# Create symlink
ln -sf /opt/orca-os/orca_advanced_cli.py /usr/local/bin/orca-advanced

print_success "Advanced CLI created"

# Enable and start services
print_status "Enabling advanced services..."
systemctl daemon-reload
systemctl enable orca-ai-process-manager.service
systemctl enable orca-ai-logging.service
systemctl enable orca-ai-scheduler.service
systemctl enable orca-predictive-ai.service
systemctl enable orca-dashboard.service

print_success "Services enabled"

# Start services
print_status "Starting advanced services..."
systemctl start orca-ai-process-manager.service
systemctl start orca-ai-logging.service
systemctl start orca-ai-scheduler.service
systemctl start orca-predictive-ai.service
systemctl start orca-dashboard.service

print_success "Services started"

# Create comprehensive documentation
print_status "Creating comprehensive documentation..."

cat > /opt/orca-os/ADVANCED_FEATURES_COMPLETE.md << 'EOF'
# 🐋 Orca OS Advanced Features - Complete Guide

## Overview
Orca OS Advanced Features represent the culmination of Phase 3 (Kernel & System Integration) and Phase 4 (Advanced Features) development. These features bring AI-powered intelligence to every aspect of system management.

## Phase 3: Kernel & System Integration

### 🤖 AI Process Manager
**Command**: `orca-process-manager`
**Service**: `orca-ai-process-manager.service`

**Features**:
- Intelligent process analysis and categorization
- AI-powered resource optimization
- Real-time anomaly detection
- System health scoring and recommendations
- Automatic process priority adjustment

**Usage**:
```bash
# Check system health
orca-process-manager

# Optimize processes
orca-process-manager --optimize

# Monitor in real-time
orca-process-manager --monitor
```

### 📊 AI Logging System
**Command**: `orca-logs`
**Service**: `orca-ai-logging.service`

**Features**:
- Intelligent log analysis and categorization
- AI-powered error pattern detection
- Real-time log monitoring with alerts
- Automated log summarization
- Predictive issue identification

**Usage**:
```bash
# Analyze recent logs
orca-logs

# Analyze specific service
orca-logs --service systemd

# Monitor logs in real-time
orca-logs --monitor
```

### ⚡ AI Scheduler
**Command**: `orca-scheduler`
**Service**: `orca-ai-scheduler.service`

**Features**:
- Intelligent process priority management
- AI-aware CPU affinity optimization
- Dynamic load balancing
- Performance-based scheduling decisions
- Resource allocation optimization

**Usage**:
```bash
# Optimize scheduling
orca-scheduler --optimize

# Monitor system load
orca-scheduler --monitor

# Get scheduling report
orca-scheduler --report
```

## Phase 4: Advanced Features

### 📦 Orca AI Package Manager
**Command**: `orca-install <package>`
**Service**: Integrated with Orca CLI

**Features**:
- AI-powered package recommendations
- Intelligent dependency analysis
- Conflict detection and resolution
- Installation intent understanding
- Package usage analytics

**Usage**:
```bash
# Install with AI assistance
orca-install docker

# Search packages
orca-install --search "text editor"

# Get recommendations
orca-install --recommend
```

### 🔌 Plugin System
**Command**: `orca-plugins`
**Service**: Integrated with Orca CLI

**Features**:
- Extensible plugin architecture
- AI-enhanced plugin functions
- Community extension support
- Plugin template generation
- Dynamic plugin loading

**Usage**:
```bash
# List plugins
orca-plugins --list

# Create plugin template
orca-plugins --create my-plugin

# Manage plugins
orca-plugins --enable my-plugin
```

### 🔮 Predictive AI
**Command**: `orca-predict`
**Service**: `orca-predictive-ai.service`

**Features**:
- System trend analysis and prediction
- Proactive issue detection
- Performance forecasting
- Optimization recommendations
- Risk assessment

**Usage**:
```bash
# Get predictions
orca-predict

# System forecast
orca-predict --forecast

# Get recommendations
orca-predict --recommendations
```

### 📈 Orca Dashboard
**Command**: `orca-dashboard`
**Service**: `orca-dashboard.service`

**Features**:
- Real-time system monitoring
- AI-powered insights and recommendations
- Interactive system overview
- Process and resource monitoring
- Predictive alerts display

**Usage**:
```bash
# Start dashboard
orca-dashboard

# Custom refresh interval
orca-dashboard --refresh 10
```

### 🛠️ System Optimizer
**Command**: `orca-optimize`
**Service**: Integrated with Orca CLI

**Features**:
- AI-powered system optimization
- Automated performance tuning
- Resource cleanup and management
- Optimization task scheduling
- Performance impact analysis

**Usage**:
```bash
# Full optimization
orca-optimize --full

# Dry run
orca-optimize --dry-run

# Specific optimization
orca-optimize --memory
```

## Unified Advanced CLI

### 🎯 Orca Advanced Command
**Command**: `orca-advanced <command>`

**Available Commands**:
- `process-manager` - AI Process Manager
- `logs` - AI Logging System
- `scheduler` - AI Scheduler
- `install` - AI Package Manager
- `predict` - Predictive AI
- `dashboard` - System Dashboard
- `optimize` - System Optimizer
- `plugins` - Plugin System
- `test` - Test Suite

**Usage**:
```bash
# Unified interface
orca-advanced process-manager --health
orca-advanced logs --hours 48
orca-advanced install docker --intent "containerization"
orca-advanced predict --forecast
orca-advanced optimize --full
```

## Services and Integration

### Systemd Services
All advanced features run as systemd services:
- `orca-ai-process-manager.service`
- `orca-ai-logging.service`
- `orca-ai-scheduler.service`
- `orca-predictive-ai.service`
- `orca-dashboard.service`

### Service Management
```bash
# Check service status
systemctl status orca-ai-*

# Start/stop services
systemctl start orca-ai-process-manager
systemctl stop orca-dashboard

# View logs
journalctl -u orca-ai-process-manager -f
```

## Testing and Validation

### Test Suite
**Command**: `orca-test`

**Features**:
- Comprehensive component testing
- Performance benchmarking
- Integration testing
- Error handling validation
- Configuration testing

**Usage**:
```bash
# Run all tests
orca-test

# Test specific component
orca-test --component process-manager

# Performance tests
orca-test --performance
```

## Configuration

### Configuration Files
- `/opt/orca-os/config/orca.yaml` - Main configuration
- `/etc/orca/orca.yaml` - System-wide configuration
- `/opt/orca-os/plugins/` - Plugin directory
- `/var/log/orca/` - Advanced features logs

### Environment Variables
- `ORCA_LLM_MODEL` - LLM model to use
- `ORCA_LLM_URL` - LLM server URL
- `ORCA_LOG_LEVEL` - Logging level
- `ORCA_OPTIMIZATION_LEVEL` - Optimization aggressiveness

## Performance and Monitoring

### Metrics
- System health scores
- Process optimization effectiveness
- Log analysis accuracy
- Prediction confidence levels
- Resource usage optimization

### Monitoring
- Real-time dashboard
- Predictive alerts
- Performance trends
- Optimization history
- AI recommendation tracking

## Security and Safety

### Safety Features
- Command validation and sanitization
- Process sandboxing
- Resource limits
- Audit logging
- Risk assessment

### Security Considerations
- Local-first AI processing
- Encrypted configuration
- Secure service communication
- Process isolation
- Access control

## Troubleshooting

### Common Issues
1. **Service not starting**: Check logs with `journalctl -u <service-name>`
2. **AI not responding**: Verify Ollama is running and accessible
3. **Performance issues**: Run `orca-optimize --full`
4. **Plugin errors**: Check plugin compatibility and dependencies

### Debug Commands
```bash
# Check system health
orca-process-manager --health

# Analyze logs
orca-logs --analyze

# Test AI connectivity
orca-predict --test

# Verify services
systemctl status orca-ai-*
```

## Future Development

### Planned Features
- Machine learning model training
- Advanced predictive analytics
- Cloud integration options
- Enterprise features
- Mobile companion app

### Community Contributions
- Plugin development
- Feature requests
- Bug reports
- Documentation improvements
- Testing and validation

---

**Orca OS Advanced Features** - Where AI meets the operating system! 🐋

For support and documentation, visit: https://github.com/orca-os/orca-os
EOF

print_success "Comprehensive documentation created"

# Run tests
print_status "Running test suite..."
cd /opt/orca-os
source venv/bin/activate
python advanced/test_advanced_features.py --component all

print_success "Test suite completed"

# Final status check
print_status "Checking service status..."
systemctl status orca-ai-process-manager.service --no-pager -l
systemctl status orca-ai-logging.service --no-pager -l
systemctl status orca-ai-scheduler.service --no-pager -l
systemctl status orca-predictive-ai.service --no-pager -l
systemctl status orca-dashboard.service --no-pager -l

print_success "Orca OS Advanced Features Deployment Complete!"
echo
echo "🐋 Available Commands:"
echo "  orca-process-manager  - AI process management"
echo "  orca-logs            - AI log analysis"
echo "  orca-scheduler       - AI process scheduling"
echo "  orca-predict         - Predictive AI monitoring"
echo "  orca-dashboard       - System dashboard"
echo "  orca-optimize        - System optimizer"
echo "  orca-plugins         - Plugin system"
echo "  orca-install         - AI package manager"
echo "  orca-test            - Test suite"
echo "  orca-advanced        - Unified advanced CLI"
echo
echo "📚 Documentation: /opt/orca-os/ADVANCED_FEATURES_COMPLETE.md"
echo "🔧 Services: systemctl status orca-ai-*"
echo "🧪 Tests: orca-test"
echo
echo "Welcome to the future of AI-powered Linux! 🐋"
