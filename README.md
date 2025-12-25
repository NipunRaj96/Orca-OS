# 🐋 Orca OS - AI-Native Operating System

<div align="center">

**Talk to your computer in plain English. It understands you.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-yellow.svg)]()

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Tech Stack](#-tech-stack)

</div>

---

## 🌟 What is Orca OS?

**Orca OS is an AI-powered operating system wrapper that lets you control your computer using natural language.**

Instead of memorizing complex commands, just **talk to your computer in plain English**. Orca understands what you want and does it for you.

### 🎯 The Vision

Imagine if you could say:
- *"Show me my system health"* instead of `top` or `htop`
- *"Organize my downloads folder"* instead of manually sorting files
- *"Optimize my system"* instead of running multiple optimization commands
- *"Show me my usage patterns"* instead of analyzing logs manually

**That's Orca OS.**

---

## ✨ Key Features

### 🗣️ Natural Language Interface
Control your entire system using plain English. No command memorization needed.

```bash
python3 -m orca.cli "show me disk usage"
python3 -m orca.cli "organize my downloads"
python3 -m orca.cli "optimize my system"
```

### 🏥 System Health Monitoring
Get real-time health scores and recommendations for your system.

- **Performance Score** - CPU, memory, disk performance
- **Security Score** - System security assessment
- **Stability Score** - System reliability metrics
- **Efficiency Score** - Resource utilization
- **Smart Recommendations** - Actionable insights

```bash
python3 -m orca.cli "show health score"
```

### 📁 Smart File Organization
Automatically organize files by type, category, and usage patterns.

- Intelligent file categorization
- Automatic folder creation
- Preview before organizing
- Safe file movement
- Pattern recognition

```bash
python3 -m orca.cli "organize my downloads"
```

### 📊 Usage Analytics & Insights
Understand your computing patterns and improve productivity.

- Command usage statistics
- Productivity metrics
- Peak activity analysis
- Usage trends
- Personalized insights

```bash
python3 -m orca.cli "show my usage patterns"
```

### 🔧 Autonomous System Optimization
Let Orca automatically detect and fix system issues.

- Proactive issue detection
- Automatic fixes
- Performance optimization
- Resource management
- Self-healing capabilities

```bash
python3 -m orca.cli "optimize my system"
```

### 💬 Interactive Chat Mode
Have conversations with your operating system.

- Multi-turn conversations
- Context awareness
- Command history
- Built-in help system

```bash
python3 -m orca.cli --interactive
```

### 📝 Command History & Favorites
Never lose a command again. Save and reuse your favorite commands.

- Browse command history
- Search past commands
- Save favorites
- Quick execution
- Command templates

```bash
python3 -m orca.cli --history
python3 -m orca.cli --favorites
```

### 🤖 Intelligent Routing
Orca automatically routes your queries to the right features.

- Automatic feature detection
- Smart query understanding
- Context-aware responses
- Multi-feature coordination

### 🧠 Learning & Adaptation
Orca learns from your usage patterns and gets smarter over time.

- Pattern recognition
- Failure learning
- Usage optimization
- Personalized suggestions

### 🛡️ Security First
All commands are validated and sandboxed before execution.

- Command validation
- Risk assessment
- User confirmation
- Safe execution environment

---

## 🚀 Quick Start

# 1. Clone the repository
git clone <repository-url>
cd Orca-OS

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Install Ollama (AI backend)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2

# 4. Start Ollama (keep this running)
ollama serve

# 5. In a NEW terminal, try it:
orca "show me disk usage"

**That's it!** You're now using AI to control your computer.

### Try These Commands

```bash
# System information
python3 -m orca.cli "show me system information"

# Health check
python3 -m orca.cli "show health score"

# Organize files
python3 -m orca.cli "organize my downloads"

# Usage analytics
python3 -m orca.cli "show my usage patterns"

# System optimization
python3 -m orca.cli "optimize my system"

# Interactive mode
python3 -m orca.cli --interactive
```

---

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+** - Core language
- **Ollama** - Local LLM inference engine
- **LLaMA 3.2** - AI model for natural language understanding
- **SQLAlchemy** - Database ORM
- **SQLite** - Lightweight database
- **Click** - CLI framework
- **Rich** - Beautiful terminal UI

### Key Libraries
- **psutil** - System monitoring
- **Pydantic** - Data validation
- **FastAPI** - API framework (for daemon)
- **LangChain** - LLM integration utilities

### Architecture
- **Modular Design** - Feature-based architecture
- **Intelligent Router** - Smart query routing
- **Autonomous Engine** - Self-healing and optimization
- **Analytics Engine** - Usage tracking and insights
- **Security Layer** - Command validation and sandboxing

---

## 📚 Documentation

Comprehensive documentation for users of all levels:

- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - Get started in 5 minutes
- **[Complete User Journey](docs/COMPLETE_USER_JOURNEY_GUIDE.md)** - Beginner-friendly guide to all features
- **[Implementation Tracker](docs/TRACKER.md)** - Development progress and feature documentation
- **[Codebase Analysis](docs/COMPREHENSIVE_CODEBASE_ANALYSIS.md)** - Technical deep dive

---

## 🎯 Use Cases

### For Non-Technical Users
- Control your computer without learning commands
- Get system insights in plain English
- Automate file organization
- Monitor system health easily

### For Developers
- Faster system management
- Automated optimization
- Usage analytics
- Productivity insights

### For System Administrators
- Intelligent system monitoring
- Proactive issue detection
- Automated maintenance
- Comprehensive analytics

---

## 🔮 What Makes This Special?

### 1. **True Natural Language Understanding**
Not just keyword matching - Orca understands context and intent.

### 2. **Autonomous Capabilities**
Orca doesn't just execute commands - it thinks, learns, and acts autonomously.

### 3. **Comprehensive Feature Set**
Not just a command wrapper - a complete system management suite.

### 4. **User-Centric Design**
Built for real users, not just developers.

### 5. **Continuous Learning**
Gets smarter with every interaction.

---

## 🎨 Features Overview

| Feature | Description | Status |
|---------|-------------|--------|
| Natural Language Interface | Control system with plain English | ✅ Complete |
| System Health Monitoring | Real-time health scores and recommendations | ✅ Complete |
| Smart File Organization | Automatic file sorting and organization | ✅ Complete |
| Usage Analytics | Productivity insights and patterns | ✅ Complete |
| System Optimization | Autonomous system fixes and optimization | ✅ Complete |
| Interactive Chat Mode | Conversational interface | ✅ Complete |
| Command History | Browse and search past commands | ✅ Complete |
| Favorites System | Save and reuse favorite commands | ✅ Complete |
| Command Templates | Pre-built command templates | ✅ Complete |
| Self-Healing | Automatic issue detection and fixing | ✅ Complete |
| Failure Learning | Learns from mistakes and improves | ✅ Complete |
| Response Caching | Fast response times with caching | ✅ Complete |

---

### Areas for Contribution
- Feature development
- Documentation improvements
- Bug fixes
- Testing
- Performance optimization

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">

[Get Started](docs/QUICK_START_GUIDE.md) • [Learn More](docs/COMPLETE_USER_JOURNEY_GUIDE.md) • [View Features](#-features)

</div>
