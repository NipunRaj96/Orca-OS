"""
Policy engine for Orca OS.
"""

from typing import Dict, Any
from ..core.models import CommandSuggestion, CommandAction, CommandRisk, PolicyConfig


class PolicyEngine:
    """Policy engine for command validation and risk assessment."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize policy engine."""
        self.config = PolicyConfig(**config)
        self.rules = self._build_default_rules()
    
    def validate(self, suggestion: CommandSuggestion) -> CommandSuggestion:
        """Validate command against policies."""
        # Apply confidence threshold
        if suggestion.confidence < self.config.max_confidence_threshold:
            return CommandSuggestion(
                command=suggestion.command,
                confidence=suggestion.confidence,
                action=CommandAction.CLARIFY,
                risk_level=suggestion.risk_level,
                explanation=f"Confidence below threshold ({suggestion.confidence:.2%} < {self.config.max_confidence_threshold:.2%})",
                context_used=suggestion.context_used
            )
        
        # Apply sandbox requirement
        if self.config.sandbox_all_commands and suggestion.action == CommandAction.EXECUTE:
            # Keep as execute but will be sandboxed
            pass
        
        return suggestion
    
    def _build_default_rules(self) -> list:
        """Build default policy rules."""
        return [
            {
                "name": "read_only_safe",
                "pattern": r"^(ls|ps|df|du|free|uptime|whoami|pwd|cat|head|tail|grep|find|which|date|cal|echo|printf|wc|sort|uniq|history|env|printenv|id|groups|last)\b",
                "action": CommandAction.EXECUTE,
                "risk_level": CommandRisk.SAFE,
                "description": "Safe read-only commands",
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