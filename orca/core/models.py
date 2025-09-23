"""
Core data models for Orca OS.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class CommandAction(str, Enum):
    """Available actions for command execution."""
    EXECUTE = "execute"
    DRY_RUN = "dry_run"
    CLARIFY = "clarify"
    BLOCKED = "blocked"
    READ = "read"


class CommandRisk(str, Enum):
    """Risk levels for commands."""
    SAFE = "safe"  # Read-only operations
    MODERATE = "moderate"  # Non-destructive writes
    HIGH = "high"  # Potentially destructive
    CRITICAL = "critical"  # System-level changes


class CommandSuggestion(BaseModel):
    """AI-generated command suggestion."""
    command: str = Field(..., description="The suggested command to execute")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    action: CommandAction = Field(..., description="Recommended action")
    risk_level: CommandRisk = Field(..., description="Risk assessment")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    context_used: List[str] = Field(default_factory=list, description="Context sources used")
    
    @validator('command')
    def validate_command(cls, v):
        if not v or not v.strip():
            raise ValueError("Command cannot be empty")
        return v.strip()


class ExecutionResult(BaseModel):
    """Result of command execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    sandbox_used: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserQuery(BaseModel):
    """User query with context."""
    query: str = Field(..., description="Natural language query")
    user_id: str = Field(default="default", description="User identifier")
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Session ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemContext(BaseModel):
    """System state context for LLM."""
    processes: List[Dict[str, Any]] = Field(default_factory=list)
    disk_usage: Dict[str, Any] = Field(default_factory=dict)
    recent_commands: List[str] = Field(default_factory=list)
    open_windows: List[str] = Field(default_factory=list)
    memory_usage: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(BaseModel):
    """Audit log entry."""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    session_id: str
    query: str
    suggestion: Optional[CommandSuggestion]
    result: Optional[ExecutionResult]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None


class PolicyRule(BaseModel):
    """Policy rule for command validation."""
    name: str
    pattern: str
    action: CommandAction
    risk_level: CommandRisk
    description: str
    enabled: bool = True


class PolicyConfig(BaseModel):
    """Policy configuration."""
    rules: List[PolicyRule] = Field(default_factory=list)
    default_action: str = "clarify"
    require_confirmation: bool = True
    max_confidence_threshold: float = 0.8
    sandbox_all_commands: bool = False
