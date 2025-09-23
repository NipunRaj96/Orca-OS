"""
Command validator for Orca OS.

Validates and sanitizes commands before execution.
"""

import re
import shlex
from typing import List, Tuple
from ..core.models import CommandSuggestion, CommandAction, CommandRisk, PolicyConfig


class CommandValidator:
    """Validates commands for safety and policy compliance."""
    
    def __init__(self, policy_config: PolicyConfig):
        """Initialize validator with policy configuration."""
        self.policy = policy_config
        self.rules = self._build_default_rules()
        self.dangerous_patterns = self._build_dangerous_patterns()
        self.safe_commands = self._build_safe_commands()
    
    def validate(self, suggestion: CommandSuggestion) -> CommandSuggestion:
        """Validate a command suggestion against policies."""
        # Start with the original suggestion
        validated = suggestion.model_copy()
        
        # Check for dangerous patterns
        if self._is_dangerous(suggestion.command):
            validated.action = CommandAction.BLOCKED
            validated.risk_level = CommandRisk.CRITICAL
            validated.explanation = "Command contains dangerous patterns and is blocked"
            return validated
        
        # Check against policy rules
        policy_result = self._check_policy_rules(suggestion)
        if policy_result.action != CommandAction.EXECUTE:
            validated.action = policy_result.action
            validated.risk_level = policy_result.risk_level
            validated.explanation = policy_result.explanation
            return validated
        
        # Apply confidence threshold
        if suggestion.confidence < self.policy.max_confidence_threshold:
            validated.action = CommandAction.CLARIFY
            validated.explanation = f"Confidence too low ({suggestion.confidence:.2%})"
        
        return validated
    
    def _is_dangerous(self, command: str) -> bool:
        """Check if command contains dangerous patterns."""
        command_lower = command.lower().strip()
        
        # Check against dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command_lower):
                return True
        
        return False
    
    def _check_policy_rules(self, suggestion: CommandSuggestion) -> CommandSuggestion:
        """Check command against policy rules."""
        command = suggestion.command
        
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
                
            if re.search(rule["pattern"], command, re.IGNORECASE):
                return CommandSuggestion(
                    command=command,
                    confidence=suggestion.confidence,
                    action=CommandAction(rule["action"]),
                    risk_level=CommandRisk(rule["risk_level"]),
                    explanation=f"Matched policy rule: {rule['description']}",
                    context_used=suggestion.context_used
                )
        
        # Default policy
        return CommandSuggestion(
            command=command,
            confidence=suggestion.confidence,
            action=self.policy.default_action,
            risk_level=CommandRisk.SAFE,
            explanation="No specific policy rule matched",
            context_used=suggestion.context_used
        )
    
    def _build_dangerous_patterns(self) -> List[str]:
        """Build regex patterns for dangerous commands."""
        return [
            r'\brm\s+-rf\s+/',  # rm -rf /
            r'\bdd\s+if=',      # dd commands
            r'\bmkfs\.',        # Filesystem creation
            r'\bfdisk\b',       # Disk partitioning
            r'\bparted\b',      # Disk partitioning
            r'\bwipefs\b',      # Filesystem wiping
            r'\bchmod\s+777\s+/',  # Dangerous permissions
            r'\bchown\s+root\s+/', # Root ownership changes
            r'>\s*/dev/',       # Redirecting to device files
            r'\|\s*sh\b',       # Piping to shell
            r'\|\s*bash\b',     # Piping to bash
            r'curl\s+.*\|\s*sh', # curl | sh patterns
            r'wget\s+.*\|\s*sh', # wget | sh patterns
        ]
    
    def _build_safe_commands(self) -> List[str]:
        """Build list of generally safe commands."""
        return [
            'ls', 'ps', 'df', 'du', 'free', 'vm_stat', 'uptime', 'whoami', 'pwd',
            'cat', 'head', 'tail', 'grep', 'find', 'locate', 'which',
            'date', 'cal', 'echo', 'printf', 'wc', 'sort', 'uniq',
            'history', 'env', 'printenv', 'id', 'groups', 'last', 'uname',
            'curl', 'wget', 'scp', 'rsync'  # Download commands
        ]
    
    def _build_default_rules(self) -> list:
        """Build default policy rules."""
        return [
            {
                "name": "read_only_safe",
                "pattern": r"^(ls|ps|df|du|free|vm_stat|uptime|whoami|pwd|cat|head|tail|grep|find|which|date|cal|echo|printf|wc|sort|uniq|history|env|printenv|id|groups|last|uname)\b",
                "action": CommandAction.EXECUTE,
                "risk_level": CommandRisk.SAFE,
                "description": "Safe read-only commands",
                "enabled": True
            },
            {
                "name": "download_safe",
                "pattern": r"^(curl|wget|scp|rsync)\s+",
                "action": CommandAction.EXECUTE,
                "risk_level": CommandRisk.MODERATE,
                "description": "Safe download commands",
                "enabled": True
            },
            {
                "name": "dangerous_patterns",
                "pattern": r"(rm\s+-rf\s+/|dd\s+if=|mkfs\.|fdisk|parted|wipefs|chmod\s+777\s+/|chown\s+root\s+/)",
                "action": CommandAction.BLOCKED,
                "risk_level": CommandRisk.CRITICAL,
                "description": "Dangerous system commands",
                "enabled": True
            },
            {
                "name": "shell_piping",
                "pattern": r"(\|\s*sh\b|\|\s*bash\b|curl\s+.*\|\s*sh|wget\s+.*\|\s*sh)",
                "action": CommandAction.BLOCKED,
                "risk_level": CommandRisk.HIGH,
                "description": "Potentially dangerous shell piping",
                "enabled": True
            }
        ]
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command by removing dangerous elements."""
        # Parse command into tokens
        try:
            tokens = shlex.split(command)
        except ValueError:
            # If parsing fails, return a safe command
            return "echo 'Invalid command syntax'"
        
        if not tokens:
            return "echo 'Empty command'"
        
        # Check if it's a safe command
        if tokens[0] in self.safe_commands:
            return command
        
        # For other commands, apply basic sanitization
        # Remove any redirections to system files
        sanitized = []
        for token in tokens:
            if not (token.startswith('>') and '/dev/' in token):
                sanitized.append(token)
        
        return ' '.join(sanitized)
