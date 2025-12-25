"""
Configuration management for Orca OS.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration."""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"  # Default to llama3.1:8b (fallback if config not found)
    temperature: float = 0.1
    max_tokens: int = 512
    timeout: int = 30


class PolicyConfig(BaseModel):
    """Policy configuration."""
    require_confirmation: bool = True
    max_confidence_threshold: float = 0.8
    sandbox_all_commands: bool = True
    default_action: str = "clarify"


class ExecutorConfig(BaseModel):
    """Executor configuration."""
    use_sandbox: bool = True
    timeout: int = 30
    max_output_size: int = 1024 * 1024  # 1MB


class Config(BaseModel):
    """Main configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    executor: ExecutorConfig = Field(default_factory=ExecutorConfig)
    log_level: str = "INFO"
    data_dir: str = "~/.orca"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment."""
    if config_path and os.path.exists(config_path):
        # Load from specified file
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return Config(**config_data)
    
    # Load from environment variables
    config_data = {
        "llm": {
            "base_url": os.getenv("ORCA_LLM_URL", "http://localhost:11434"),
            "model": os.getenv("ORCA_LLM_MODEL", "llama3.1:8b"),
            "temperature": float(os.getenv("ORCA_LLM_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("ORCA_LLM_MAX_TOKENS", "512")),
            "timeout": int(os.getenv("ORCA_LLM_TIMEOUT", "30"))
        },
        "policy": {
            "require_confirmation": os.getenv("ORCA_REQUIRE_CONFIRMATION", "true").lower() == "true",
            "max_confidence_threshold": float(os.getenv("ORCA_CONFIDENCE_THRESHOLD", "0.8")),
            "sandbox_all_commands": os.getenv("ORCA_SANDBOX_COMMANDS", "true").lower() == "true",
            "default_action": os.getenv("ORCA_DEFAULT_ACTION", "clarify")
        },
        "executor": {
            "use_sandbox": os.getenv("ORCA_USE_SANDBOX", "true").lower() == "true",
            "timeout": int(os.getenv("ORCA_EXEC_TIMEOUT", "30")),
            "max_output_size": int(os.getenv("ORCA_MAX_OUTPUT", str(1024 * 1024)))
        },
        "log_level": os.getenv("ORCA_LOG_LEVEL", "INFO"),
        "data_dir": os.path.expanduser(os.getenv("ORCA_DATA_DIR", "~/.orca"))
    }
    
    return Config(**config_data)
