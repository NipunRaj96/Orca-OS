"""
Context provider for gathering system state information.
"""

import os
import subprocess
import psutil
from typing import List, Dict, Any
from ..core.models import SystemContext


class ContextProvider:
    """Provides system context for LLM prompts."""
    
    def __init__(self):
        """Initialize context provider."""
        self.max_processes = 10
        self.max_recent_commands = 5
    
    async def get_context(self) -> SystemContext:
        """Get current system context."""
        try:
            context = SystemContext()
            
            # Get processes
            context.processes = await self._get_processes()
            
            # Get disk usage
            context.disk_usage = await self._get_disk_usage()
            
            # Get recent commands
            context.recent_commands = await self._get_recent_commands()
            
            # Get open windows (if available)
            context.open_windows = await self._get_open_windows()
            
            # Get memory usage
            context.memory_usage = await self._get_memory_usage()
            
            return context
            
        except Exception as e:
            # Return minimal context on error
            return SystemContext()
    
    async def _get_processes(self) -> List[Dict[str, Any]]:
        """Get top processes by CPU usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] is not None:
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and limit
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:self.max_processes]
            
        except Exception:
            return []
    
    async def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            return disk_usage
            
        except Exception:
            return {}
    
    async def _get_recent_commands(self) -> List[str]:
        """Get recent shell commands."""
        try:
            # Try to get history from common shell history files
            history_files = [
                os.path.expanduser("~/.bash_history"),
                os.path.expanduser("~/.zsh_history"),
                os.path.expanduser("~/.fish_history")
            ]
            
            commands = []
            for history_file in history_files:
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            # Get last few commands, skip empty lines
                            recent = [line.strip() for line in lines[-self.max_recent_commands:] if line.strip()]
                            commands.extend(recent)
                            break  # Use first available history file
                    except (PermissionError, UnicodeDecodeError):
                        continue
            
            return commands[-self.max_recent_commands:]  # Return last N commands
            
        except Exception:
            return []
    
    async def _get_open_windows(self) -> List[str]:
        """Get open window titles (X11/Wayland)."""
        try:
            # This is a simplified implementation
            # In a real implementation, you'd use X11/Wayland APIs
            windows = []
            
            # Try to get window list using wmctrl if available
            try:
                result = subprocess.run(
                    ['wmctrl', '-l'], 
                    capture_output=True, 
                    text=True, 
                    timeout=2
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            # Extract window title (everything after the desktop number)
                            parts = line.split(None, 3)
                            if len(parts) >= 4:
                                title = parts[3]
                                if title and title != 'N/A':
                                    windows.append(title)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return windows[:5]  # Limit to 5 windows
            
        except Exception:
            return []
    
    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'free': memory.free
            }
        except Exception:
            return {}
