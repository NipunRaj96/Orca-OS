"""
Prompt management for Orca OS.

Handles structured prompt generation with safety guardrails.
"""

from typing import List, Dict, Any
from ..core.models import UserQuery, SystemContext, CommandAction, CommandRisk


class PromptManager:
    """Manages prompt generation and safety guardrails."""
    
    def __init__(self):
        """Initialize prompt manager."""
        self.system_prompt = self._build_system_prompt()
        self.safety_guardrails = self._build_safety_guardrails()
    
    def build_command_prompt(self, query: UserQuery, context: SystemContext) -> str:
        """Build a structured prompt for command generation."""
        
        # Simple, direct prompt that works better with LLaMA
        prompt = f"""User: {query.query}

Examples:
Query: "show me disk usage" → {{"command": "df -h", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Shows disk usage in human-readable format"}}
Query: "check memory usage" → {{"command": "vm_stat", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Shows memory usage on macOS"}}
Query: "check my computer's memory usage" → {{"command": "vm_stat", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Shows memory usage on macOS"}}
Query: "list running processes" → {{"command": "ps aux --sort=-%cpu | head -10", "confidence": 0.90, "action": "execute", "risk_level": "safe", "explanation": "Shows top 10 processes by CPU usage"}}
Query: "show me what programs are running" → {{"command": "ps aux --sort=-%cpu | head -10", "confidence": 0.90, "action": "execute", "risk_level": "safe", "explanation": "Shows top 10 processes by CPU usage"}}
Query: "show me the folders in my home directory" → {{"command": "ls -la ~", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Lists all files and folders in home directory"}}
Query: "navigate to Macintosh HD and show Users folder" → {{"command": "ls -la /Users", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Lists contents of Users directory"}}
Query: "show system information" → {{"command": "uname -a", "confidence": 0.90, "action": "execute", "risk_level": "safe", "explanation": "Shows system information"}}
Query: "download a file from the internet" → {{"command": "curl -O https://example.com/file.txt", "confidence": 0.85, "action": "execute", "risk_level": "moderate", "explanation": "Downloads file using curl"}}
Query: "download Python installer" → {{"command": "curl -O https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg", "confidence": 0.80, "action": "execute", "risk_level": "moderate", "explanation": "Downloads Python installer for macOS"}}

Command mappings:
- Memory queries → "vm_stat" (macOS) or "free -m" (Linux)
- Disk queries → "df -h"
- Process queries → "ps aux" or "top"
- System info → "uname -a"
- Download queries → "curl -O" or "wget"

Respond with ONLY this JSON format:
{{"command": "vm_stat", "confidence": 0.95, "action": "execute", "risk_level": "safe", "explanation": "Shows memory usage on macOS"}}

Response:"""
        
        return prompt
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt defining Orca's role."""
        return """You are Orca, an AI assistant that helps users with Linux system tasks. Your role is to:

1. Translate natural language requests into appropriate Linux commands
2. Assess the risk level of suggested commands
3. Provide safe, helpful system assistance
4. Always prioritize user safety and system integrity

You have access to current system context and should use it to provide relevant, accurate suggestions."""
    
    def _build_safety_guardrails(self) -> str:
        """Build safety guardrails for command generation."""
        return """SAFETY RULES:
- NEVER suggest commands that could damage the system (rm -rf /, dd, mkfs, etc.)
- NEVER suggest commands that require root privileges unless explicitly requested
- ALWAYS prefer read-only operations when possible
- ALWAYS use dry_run for potentially destructive operations
- ALWAYS explain what a command does before suggesting execution
- NEVER suggest commands that could expose sensitive data
- ALWAYS validate file paths and avoid wildcards in destructive operations

RISK LEVELS:
- safe: Read-only operations (ls, ps, df, cat, head, tail, grep)
- moderate: Non-destructive writes (mkdir, touch, cp, mv within home)
- high: Potentially destructive (rm, chmod, system config changes)
- critical: System-level changes (format, kernel, bootloader)

ACTIONS:
- execute: Safe to run immediately
- dry_run: Show what would happen without executing
- clarify: Request more information from user
- blocked: Command violates safety rules"""
    
    def _format_context(self, context: SystemContext) -> str:
        """Format system context for the prompt."""
        context_parts = []
        
        if context.processes:
            context_parts.append("TOP PROCESSES:")
            for proc in context.processes[:5]:  # Limit to top 5
                context_parts.append(f"  {proc.get('name', 'unknown')}: {proc.get('cpu_percent', 0):.1f}% CPU")
        
        if context.disk_usage:
            context_parts.append("DISK USAGE:")
            for mount, usage in context.disk_usage.items():
                context_parts.append(f"  {mount}: {usage.get('percent', 0):.1f}% used")
        
        if context.recent_commands:
            context_parts.append("RECENT COMMANDS:")
            for cmd in context.recent_commands[-3:]:  # Last 3 commands
                context_parts.append(f"  {cmd}")
        
        if context.memory_usage:
            context_parts.append("MEMORY USAGE:")
            context_parts.append(f"  Available: {context.memory_usage.get('available', 0)} MB")
        
        return "\n".join(context_parts) if context_parts else "No context available"
    
    def get_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Get few-shot examples for better command generation."""
        return [
            {
                "query": "show me what's using the most CPU",
                "response": {
                    "command": "ps aux --sort=-%cpu | head -n 10",
                    "confidence": 0.95,
                    "action": "execute",
                    "risk_level": "safe",
                    "explanation": "Shows the top 10 processes by CPU usage",
                    "context_used": ["processes"]
                }
            },
            {
                "query": "check disk space",
                "response": {
                    "command": "df -h",
                    "confidence": 0.98,
                    "action": "execute",
                    "risk_level": "safe",
                    "explanation": "Shows disk usage in human-readable format",
                    "context_used": ["disk_usage"]
                }
            },
            {
                "query": "find large files in my home directory",
                "response": {
                    "command": "find ~ -type f -size +100M -exec ls -lh {} \\;",
                    "confidence": 0.85,
                    "action": "dry_run",
                    "risk_level": "moderate",
                    "explanation": "Finds files larger than 100MB in home directory (dry run for safety)",
                    "context_used": ["disk_usage"]
                }
            }
        ]
