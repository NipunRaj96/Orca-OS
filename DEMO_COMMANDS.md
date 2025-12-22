# 🐋 Orca OS - Demonstration Commands

## ✅ Best Working Commands for Presentation

### 1. System Monitoring Commands

```bash
# Disk Usage
python3 orca_os.py "show me disk usage"
# → Generates: df -h
# → Shows: Complete disk usage with all partitions

# Memory Usage  
python3 orca_os.py "check memory usage"
# → Generates: vm_stat
# → Shows: Detailed memory statistics

# System Information
python3 orca_os.py "show me system information"
# → Generates: uname -a
# → Shows: System kernel and version info
```

### 2. File Operations

```bash
# List Current Directory
python3 orca_os.py "list all files in the current directory"
# → Generates: ls -a
# → Shows: All files including hidden ones

# Home Directory Contents
python3 orca_os.py "show me the folders in my home directory"
# → Generates: ls -la ~
# → Shows: Complete home directory listing

# Current Working Directory
python3 orca_os.py "display the current working directory"
# → Generates: pwd
# → Shows: Current directory path
```

### 3. Process Management

```bash
# Top CPU Processes
python3 orca_os.py "show me the top 5 processes using the most CPU"
# → Generates: ps aux --sort=-%cpu | head -10
# → Shows: Processes sorted by CPU usage

# Running Processes
python3 orca_os.py "show me running processes"
# → Generates: ps aux
# → Shows: All running processes
```

### 4. Advanced Queries

```bash
# Disk Space Analysis
python3 orca_os.py "show me what's taking up space on my disk"
# → Generates: df -h
# → Shows: Disk usage breakdown

# Memory Check
python3 orca_os.py "check how much memory is available"
# → Generates: vm_stat
# → Shows: Memory statistics
```

## 🎯 Presentation Flow

### Demo Sequence:

1. **Start with Simple Query**
   ```bash
   python3 orca_os.py "show me disk usage"
   ```
   - Shows natural language understanding
   - Demonstrates AI command generation
   - Shows successful execution

2. **Show File Operations**
   ```bash
   python3 orca_os.py "list all files in the current directory"
   ```
   - Demonstrates context awareness
   - Shows file system interaction

3. **System Information**
   ```bash
   python3 orca_os.py "display the current working directory"
   ```
   - Simple, reliable command
   - Quick response time

4. **Home Directory Navigation**
   ```bash
   python3 orca_os.py "show me the folders in my home directory"
   ```
   - Shows path understanding (~ expansion)
   - Demonstrates file listing

5. **Memory Monitoring**
   ```bash
   python3 orca_os.py "check memory usage"
   ```
   - System resource monitoring
   - Detailed output

## 📊 Expected Results

All commands should:
- ✅ Generate appropriate Linux/macOS commands
- ✅ Execute successfully
- ✅ Show formatted output
- ✅ Complete in 2-5 seconds
- ✅ Display confidence scores (85-95%)

## 🔧 Setup for Demo

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure Ollama is running
curl http://localhost:11434/api/tags

# Run commands
python3 orca_os.py "your query here"
```

