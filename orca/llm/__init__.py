"""
LLM integration module for Orca OS.
"""

from .manager import LLMManager
from .prompts import PromptManager

__all__ = ["LLMManager", "PromptManager"]
