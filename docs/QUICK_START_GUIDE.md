# 🚀 Orca OS - Quick Start Guide
## Get Started in 5 Minutes - No Technical Knowledge Required!

---

## ⚡ Super Quick Start (5 Minutes)

### Step 1: Install (2 minutes)
```bash
git clone https://github.com/NipunRaj96/Orca-OS.git
cd Orca-OS
pip install -r requirements.txt
python3 -m orca.database.init_db
```

### Step 2: Set Up AI (2 minutes)
```bash
# Install Ollama (if not installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# In a NEW terminal, download the AI model
ollama pull llama3.2
```

### Step 3: Try It! (1 minute)
```bash
python3 -m orca.cli "show me the current time"
```

**🎉 Done! You're using Orca OS!**

---

## 📱 How to Use Orca OS

### 1️⃣ **Basic Commands (Easiest Way)**
Just type your question in plain English:
```bash
python3 -m orca.cli "your question here"
```

**Examples:**
```bash
python3 -m orca.cli "show me disk usage"
python3 -m orca.cli "what's my system health"
python3 -m orca.cli "organize my downloads folder"
```

### 2️⃣ **Interactive Chat Mode (Conversation)**
Have a conversation with Orca:
```bash
python3 -m orca.cli --interactive
```

Then chat naturally:
```
You: show me disk usage
Orca: [Shows disk usage]

You: organize my downloads
Orca: [Organizes your downloads]

You: exit
```

### 3️⃣ **View Your History**
See all your past commands:
```bash
python3 -m orca.cli --history
```

---

## 🎯 Your First 10 Commands (Try These!)

### Basic System Info
1. **System Information:**
   ```bash
   python3 -m orca.cli "show me system information"
   ```

2. **Disk Usage:**
   ```bash
   python3 -m orca.cli "show me disk usage"
   ```

3. **Memory Usage:**
   ```bash
   python3 -m orca.cli "check memory usage"
   ```

4. **Running Programs:**
   ```bash
   python3 -m orca.cli "show me running processes"
   ```

### Advanced Features
5. **System Health Score:**
   ```bash
   python3 -m orca.cli "show health score"
   ```
   See how healthy your system is (0-100 score)

6. **Organize Files:**
   ```bash
   python3 -m orca.cli "organize my downloads folder"
   ```
   Automatically sorts files into folders

7. **Usage Analytics:**
   ```bash
   python3 -m orca.cli "show my usage patterns"
   ```
   See your productivity stats and patterns

8. **System Optimization:**
   ```bash
   python3 -m orca.cli "optimize my system"
   ```
   Automatically fixes and optimizes your system

9. **View Favorites:**
   ```bash
   python3 -m orca.cli --favorites
   ```
   See your saved favorite commands

10. **Command Templates:**
    ```bash
    python3 -m orca.cli --templates
    ```
    Browse pre-built command templates

---

## 🌟 Key Features You Can Use Right Now

### 📊 **System Health Monitoring**
Check your system's health anytime:
```bash
python3 -m orca.cli "show health score"
```
- Performance score
- Security score
- Stability score
- Efficiency score
- Recommendations

### 📁 **Smart File Organization**
Organize any folder automatically:
```bash
python3 -m orca.cli "organize my downloads"
python3 -m orca.cli "organize folder at /path/to/folder"
```
- Automatically sorts files by type
- Creates organized folder structure
- Shows preview before organizing

### 📈 **Usage Analytics**
See your productivity patterns:
```bash
python3 -m orca.cli "show my usage patterns"
python3 -m orca.cli "analytics"
```
- Command usage statistics
- Peak activity hours
- Most used commands
- Productivity trends
- Insights and recommendations

### 🔧 **System Optimization**
Let Orca fix and optimize your system:
```bash
python3 -m orca.cli "optimize my system"
python3 -m orca.cli "my system is slow"
```
- Automatic issue detection
- Proactive fixes
- Performance improvements
- Resource optimization

### 💾 **Command History & Favorites**
Never lose a command again:
```bash
# View history
python3 -m orca.cli --history

# Search history
python3 -m orca.cli --history-search "organize"

# Save favorite
python3 -m orca.cli --favorite-add "organize-downloads" "organize my downloads" "files"

# Run favorite
python3 -m orca.cli --favorite-run "organize-downloads"
```

### 📝 **Command Templates**
Use pre-built templates:
```bash
# List templates
python3 -m orca.cli --templates

# Run template
python3 -m orca.cli --template-run "system-info"
   ```

---

## 💡 Pro Tips for Beginners

✅ **Talk Naturally** - Say what you want, like talking to a friend  
✅ **Be Specific** - "show disk usage" is better than "disk"  
✅ **Use Interactive Mode** - Easier for conversations  
✅ **Check History** - See what you've done before  
✅ **Save Favorites** - Save commands you use often  
✅ **Try Templates** - Use pre-built templates for common tasks  

---

## 🆘 Need Help?

### Common Issues

**Problem: "Command not found"**
```bash
# Make sure you're using:
python3 -m orca.cli "your command"
```

**Problem: "Ollama not running"**
```bash
# Start Ollama in a separate terminal:
ollama serve
```

**Problem: "Database error"**
```bash
# Initialize database:
python3 -m orca.database.init_db
```

**Problem: "Module not found"**
```bash
# Install dependencies:
pip install -r requirements.txt
```

### Get More Help
- **Full Guide:** See `docs/COMPLETE_USER_JOURNEY_GUIDE.md`
- **All Features:** See `docs/COMPLETE_USER_JOURNEY_GUIDE.md`
- **Troubleshooting:** Check the full user journey guide

---

## 🎓 What's Next?

Once you're comfortable with basics:

1. **Try Interactive Mode:** `python3 -m orca.cli --interactive`
2. **Explore All Features:** Read the complete user journey guide
3. **Save Your Favorites:** Start building your command library
4. **Check Your Analytics:** See how you're using Orca
5. **Organize Your Files:** Let Orca organize your folders

---

## 🎉 You're Ready!

**🐋 Welcome to Orca OS - Your AI Operating System!**

*Remember: Just talk to Orca in plain English. It understands you!*

**Start simple, explore gradually, and have fun!**
