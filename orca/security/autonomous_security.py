"""
Security layer for autonomous AI actions at OS level.
Critical security checks before allowing autonomous operations.
"""

import logging
import os
import subprocess
from typing import Dict, Any, List, Optional
from enum import Enum

from ..core.models import CommandSuggestion, CommandRisk, CommandAction

logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security levels for autonomous actions."""
    SAFE = "safe"  # Can execute autonomously
    REVIEW = "review"  # Requires user review
    BLOCKED = "blocked"  # Must be blocked


class AutonomousSecurity:
    """Security checks for autonomous AI actions."""
    
    # Commands that are NEVER allowed autonomously
    BLOCKED_COMMANDS = [
        'rm -rf', 'dd if=', 'mkfs', 'fdisk', 'parted',
        'chmod 777', 'chown root', 'passwd', 'useradd',
        'iptables', 'firewall', 'systemctl stop', 'systemctl disable',
        'crontab -r', 'crontab -e', 'visudo', 'su -',
        'sudo rm', 'sudo mv', 'sudo cp', 'sudo chmod',
    ]
    
    # Commands that require review
    REVIEW_COMMANDS = [
        'kill', 'pkill', 'killall', 'systemctl restart',
        'apt remove', 'apt purge', 'pip uninstall',
        'docker rm', 'docker stop', 'service stop',
    ]
    
    # Safe commands that can run autonomously
    SAFE_COMMANDS = [
        'df -h', 'free -h', 'ps aux', 'top', 'htop',
        'journalctl', 'systemctl status', 'systemctl list-units',
        'apt update', 'apt upgrade', 'apt autoremove',
        'sync', 'echo 3 > /proc/sys/vm/drop_caches',
        'find /tmp', 'du -sh', 'ls -lah',
    ]
    
    def __init__(self):
        """Initialize security layer."""
        self.max_autonomous_actions_per_hour = 10
        self.action_history = []
    
    def check_autonomous_action(
        self,
        suggestion: CommandSuggestion,
        agent_name: str
    ) -> Dict[str, Any]:
        """Check if autonomous action is safe."""
        command = suggestion.command.lower()
        
        # Check 1: Blocked commands
        if any(blocked in command for blocked in self.BLOCKED_COMMANDS):
            return {
                'allowed': False,
                'level': SecurityLevel.BLOCKED,
                'reason': 'Command is in blocked list',
                'action': CommandAction.BLOCKED
            }
        
        # Check 2: Review commands
        if any(review in command for review in self.REVIEW_COMMANDS):
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': 'Command requires user review',
                'action': CommandAction.CLARIFY
            }
        
        # Check 3: Risk level
        if suggestion.risk_level in [CommandRisk.HIGH, CommandRisk.CRITICAL]:
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': f'High risk level: {suggestion.risk_level.value}',
                'action': CommandAction.CLARIFY
            }
        
        # Check 4: Confidence threshold
        if suggestion.confidence < 0.85:
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': f'Low confidence: {suggestion.confidence:.2%}',
                'action': CommandAction.CLARIFY
            }
        
        # Check 5: Rate limiting
        if self._check_rate_limit():
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': 'Rate limit exceeded',
                'action': CommandAction.CLARIFY
            }
        
        # Check 6: Safe command patterns
        if any(safe in command for safe in self.SAFE_COMMANDS):
            return {
                'allowed': True,
                'level': SecurityLevel.SAFE,
                'reason': 'Safe command pattern',
                'action': CommandAction.EXECUTE
            }
        
        # Check 7: File system operations (restrictive)
        if self._is_filesystem_operation(command):
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': 'File system operation requires review',
                'action': CommandAction.CLARIFY
            }
        
        # Check 8: Network operations (restrictive)
        if self._is_network_operation(command):
            return {
                'allowed': False,
                'level': SecurityLevel.REVIEW,
                'reason': 'Network operation requires review',
                'action': CommandAction.CLARIFY
            }
        
        # Default: Review required
        return {
            'allowed': False,
            'level': SecurityLevel.REVIEW,
            'reason': 'Unknown command pattern',
            'action': CommandAction.CLARIFY
        }
    
    def _is_filesystem_operation(self, command: str) -> bool:
        """Check if command is a filesystem operation."""
        fs_keywords = ['rm ', 'mv ', 'cp ', 'mkdir', 'rmdir', 'touch', 'chmod', 'chown']
        return any(keyword in command for keyword in fs_keywords)
    
    def _is_network_operation(self, command: str) -> bool:
        """Check if command is a network operation."""
        net_keywords = ['curl', 'wget', 'ssh', 'scp', 'rsync', 'nc ', 'netcat']
        return any(keyword in command for keyword in net_keywords)
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        from datetime import datetime, timedelta
        
        # Remove old entries (older than 1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.action_history = [
            action for action in self.action_history
            if action['timestamp'] > cutoff
        ]
        
        # Check if limit exceeded
        return len(self.action_history) >= self.max_autonomous_actions_per_hour
    
    def record_autonomous_action(self, command: str, success: bool):
        """Record an autonomous action for rate limiting."""
        from datetime import datetime
        
        self.action_history.append({
            'timestamp': datetime.now(),
            'command': command,
            'success': success
        })
    
    def validate_command_context(self, command: str, context: Dict[str, Any]) -> bool:
        """Validate command in context of system state."""
        # Additional context-based checks
        
        # Don't allow optimizations if system is under heavy load
        if context.get('cpu_percent', 0) > 90:
            if 'optimize' in command.lower() or 'clean' in command.lower():
                logger.warning("Blocking optimization - system under heavy load")
                return False
        
        # Don't allow memory operations if memory is low
        if context.get('memory_percent', 0) > 95:
            if 'memory' in command.lower() or 'cache' in command.lower():
                logger.warning("Blocking memory operation - memory critically low")
                return False
        
        return True

