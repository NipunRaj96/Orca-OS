"""
Orca OS - AI-Powered Linux Wrapper

A system-level AI assistant that brings intelligent command generation
and execution to Linux through a privacy-first, safety-focused approach.
"""

__version__ = "0.1.0"
__author__ = "Orca OS Team"
__email__ = "team@orca-os.dev"

from .core.daemon import OrcaDaemon
from .core.executor import CommandExecutor
from .security.policy import PolicyEngine
from .llm.manager import LLMManager
from .security.validator import CommandValidator

__all__ = [
    "OrcaDaemon",
    "CommandExecutor", 
    "PolicyEngine",
    "LLMManager",
    "CommandValidator",
]
