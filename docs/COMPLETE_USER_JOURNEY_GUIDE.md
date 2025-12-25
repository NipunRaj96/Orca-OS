# 🐋 Orca OS - Complete User Journey Guide
## From Zero to Expert - A Beginner-Friendly Guide to Every Feature

---

## 📖 Table of Contents

1. [What is Orca OS?](#1-what-is-orca-os)
2. [Installation](#2-installation)
3. [Your First Command](#3-your-first-command)
4. [Basic Features](#4-basic-features)
5. [Interactive Chat Mode](#5-interactive-chat-mode)
6. [System Health Monitoring](#6-system-health-monitoring)
7. [Smart File Organization](#7-smart-file-organization)
8. [Usage Analytics](#8-usage-analytics)
9. [System Optimization](#9-system-optimization)
10. [Command History & Favorites](#10-command-history--favorites)
11. [Command Templates](#11-command-templates)
12. [Advanced Features](#12-advanced-features)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. What is Orca OS?

### 🤔 Simple Explanation

**Orca OS is like having a smart assistant built into your computer that understands plain English.**

Instead of learning complicated commands like:
```bash
df -h | grep -E '^/dev' | awk '{print $5 " " $6}'
```

You just say:
```
"Show me how much disk space I'm using"
```

**Orca OS understands you and does it for you!**

### ✨ What Makes It Special?

- 🗣️ **Natural Language** - Talk in plain English
- 🤖 **AI-Powered** - Understands what you want
- 🛡️ **Safe** - Always asks before doing dangerous things
- 📊 **Smart** - Learns your patterns and gets smarter
- 🚀 **Fast** - Gets things done quickly

---

## 2. Installation

### Step 1: Get the Code
```bash
git clone https://github.com/NipunRaj96/Orca-OS.git
cd Orca-OS
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Database
```bash
python3 -m orca.database.init_db
```

### Step 4: Install AI (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama (keep this running)
ollama serve

# In a NEW terminal, download the AI model
ollama pull llama3.2
```

### Step 5: Test It!
```bash
python3 -m orca.cli "show me the current time"
```

**🎉 You're ready to go!**

---

## 3. Your First Command

### Try This:
```bash
python3 -m orca.cli "show me disk usage"
```

**What happens:**
1. Orca thinks about your request (5-10 seconds)
2. Shows you what it will do
3. Asks for confirmation
4. Does it and shows results

**That's it!** You just used AI to control your computer!

---

## 4. Basic Features

### System Information
```bash
python3 -m orca.cli "show me system information"
```
Shows your computer's details, OS version, hardware info.

### Disk Usage
```bash
python3 -m orca.cli "show me disk usage"
```
Shows how much space you're using on each drive.

### Memory Check
```bash
python3 -m orca.cli "check memory usage"
```
Shows RAM usage and available memory.

### Running Programs
```bash
python3 -m orca.cli "show me running processes"
```
Lists all running programs with CPU and memory usage.

### Current Location
```bash
python3 -m orca.cli "where am I"
```
Shows your current folder location.

---

## 5. Interactive Chat Mode

### What is It?
Have a **conversation** with Orca instead of one command at a time.

### How to Start
```bash
python3 -m orca.cli --interactive
```

### Example Conversation:
```
🐋 Orca OS - Interactive Mode
Type 'help' for commands, 'exit' to quit

You: show me disk usage
Orca: [Shows disk usage]

You: organize my downloads
Orca: [Organizes your downloads]

You: show health score
Orca: [Shows system health]

You: exit
```

### Built-in Commands:
- `help` - Show available commands
- `history` - See conversation history
- `clear` - Clear conversation
- `exit` or `quit` - Exit interactive mode

**💡 Tip:** Interactive mode is great for multiple questions in a row!

---

## 6. System Health Monitoring

### What is It?
Get a **health score** for your system (like a report card).

### How to Use
```bash
python3 -m orca.cli "show health score"
```

### What You Get:
- **Performance Score** (0-100) - How fast your system is
- **Security Score** (0-100) - How secure your system is
- **Stability Score** (0-100) - How stable your system is
- **Efficiency Score** (0-100) - How efficiently resources are used
- **Overall Health Score** - Combined score
- **Recommendations** - What to improve

### Example Output:
```
🏥 System Health Score: 85/100

Performance: 90/100 ✅
Security: 80/100 ⚠️
Stability: 85/100 ✅
Efficiency: 85/100 ✅

💡 Recommendations:
- Update system packages
- Clear temporary files
```

**💡 Use this regularly to keep your system healthy!**

---

## 7. Smart File Organization

### What is It?
Automatically **organizes your files** into neat folders by type.

### How to Use
```bash
python3 -m orca.cli "organize my downloads"
python3 -m orca.cli "organize folder at /path/to/folder"
```

### What It Does:
1. **Analyzes** your folder
2. **Identifies** file types (images, documents, videos, etc.)
3. **Shows preview** of what will happen
4. **Asks for confirmation**
5. **Organizes** files into folders:
   - Documents/ (PDFs, Word files, etc.)
   - Images/ (photos, pictures)
   - Videos/ (movie files)
   - Data/ (spreadsheets, databases)
   - Other/ (everything else)

### Example:
```
Before:
Downloads/
  ├── photo1.jpg
  ├── document.pdf
  ├── video.mp4
  ├── spreadsheet.xlsx
  └── ...

After:
Downloads/
  ├── Images/
  │   └── photo1.jpg
  ├── Documents/
  │   └── document.pdf
  ├── Videos/
  │   └── video.mp4
  └── Data/
      └── spreadsheet.xlsx
```

**💡 Perfect for messy folders!**

---

## 8. Usage Analytics

### What is It?
See **how you use your computer** - your patterns, productivity, and insights.

### How to Use
```bash
python3 -m orca.cli "show my usage patterns"
python3 -m orca.cli "analytics"
```

### What You Get:

#### Usage Statistics
- Total commands run
- Success rate
- Average execution time
- Activity by hour of day

#### Productivity Metrics
- Today's activity
- This week's activity
- Peak hours (when you're most active)
- Most productive day

#### Top Commands
- Your most used commands
- Success rates for each
- Average time per command

#### Patterns
- When you're most active
- Common command sequences
- Usage trends over time

#### Insights & Recommendations
- Suggestions to improve productivity
- Optimization opportunities
- Usage patterns identified

### Example Output:
```
📊 Usage Statistics (Last 30 days)

Total Queries: 150
Success Rate: 95%
Peak Hours: 2:00 PM - 5:00 PM

💡 Insights:
- You're most active on weekdays
- Consider using templates for repeated tasks
```

**💡 Great for understanding your computing habits!**

---

## 9. System Optimization

### What is It?
Let Orca **automatically fix and optimize** your system.

### How to Use
```bash
python3 -m orca.cli "optimize my system"
python3 -m orca.cli "my system is slow"
python3 -m orca.cli "fix my system"
```

### What It Does:
1. **Detects** issues (high CPU, memory, disk usage)
2. **Analyzes** problems
3. **Fixes** automatically (safely)
4. **Reports** what was fixed

### What Gets Fixed:
- High CPU usage (closes resource-heavy programs)
- Memory issues (clears caches)
- Disk space (suggests cleanup)
- Performance bottlenecks
- System slowdowns

### Example:
```
You: optimize my system
Orca: 🔍 Analyzing system...
Orca: ✅ Fixed 3 issues:
      - Closed resource-heavy process
      - Cleared system cache
      - Optimized memory usage
```

**💡 Let Orca keep your system running smoothly!**

---

## 10. Command History & Favorites

### View History
See all your past commands:
```bash
python3 -m orca.cli --history
```

### Search History
Find a specific command:
```bash
python3 -m orca.cli --history-search "organize"
```

### Save Favorites
Save commands you use often:
```bash
python3 -m orca.cli --favorite-add "organize-downloads" "organize my downloads" "files"
```

### List Favorites
See your saved favorites:
```bash
python3 -m orca.cli --favorites
```

### Run Favorite
Quickly run a saved command:
```bash
python3 -m orca.cli --favorite-run "organize-downloads"
```

### Remove Favorite
```bash
python3 -m orca.cli --favorite-remove "organize-downloads"
```

**💡 Save time by saving your common commands!**

---

## 11. Command Templates

### What are Templates?
Pre-built commands for common tasks.

### List Templates
```bash
python3 -m orca.cli --templates
```

### Show Template Details
```bash
python3 -m orca.cli --template-show "system-info"
```

### Run Template
```bash
python3 -m orca.cli --template-run "system-info"
```

### Available Templates:
- **System Info** - Get system information
- **Disk Cleanup** - Clean up disk space
- **Process Management** - Manage running processes
- **Network Check** - Check network status
- **Backup** - Backup important files
- And more!

**💡 Templates make common tasks even easier!**

---

## 12. Advanced Features

### Predictive AI
Orca can **predict problems** before they happen:
```bash
python3 -m orca.cli "will my system have problems"
```

### Self-Healing
Orca **automatically fixes** issues:
```bash
python3 -m orca.cli "fix my system"
```

### Failure Learning
Orca **learns from mistakes** and gets smarter over time.

### Response Caching
Orca **remembers** previous answers for faster responses.

**💡 These work automatically - you don't need to do anything!**

---

## 13. Troubleshooting

### Problem: "Command not found"
**Solution:** Make sure you're using:
```bash
python3 -m orca.cli "your command"
```

### Problem: "Ollama not running"
**Solution:** Start Ollama in a separate terminal:
```bash
ollama serve
```

### Problem: "Database error"
**Solution:** Initialize the database:
```bash
python3 -m orca.database.init_db
```

### Problem: "Module not found"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "Slow responses"
**Solution:** 
- Make sure Ollama is running
- Check your internet connection (for first-time setup)
- Wait a few seconds - AI processing takes time

### Still Having Issues?
1. Check the [Quick Start Guide](QUICK_START_GUIDE.md)
2. Make sure all dependencies are installed
3. Verify Ollama is running
4. Check that the database is initialized

---

## 🎉 Congratulations!

You now know how to use Orca OS! 

**Remember:**
- Just talk in plain English
- Orca understands you
- Always asks before doing dangerous things
- Gets smarter over time

**Start simple, explore gradually, and have fun!**

---

## 📚 Quick Reference

### Most Common Commands:
```bash
# System info
python3 -m orca.cli "show me system information"

# Health check
python3 -m orca.cli "show health score"

# Organize files
python3 -m orca.cli "organize my downloads"

# Analytics
python3 -m orca.cli "show my usage patterns"

# Optimize
python3 -m orca.cli "optimize my system"

# Interactive mode
python3 -m orca.cli --interactive
```

### Getting Help:
```bash
python3 -m orca.cli --help
```

---

**🐋 Welcome to Orca OS - Your AI Operating System!**
