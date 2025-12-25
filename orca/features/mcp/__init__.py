"""
MCP (Model Context Protocol) integration for Orca OS.
Enables Orca to interact with external applications and services.
"""

from .client import MCPClient
from .server_registry import MCPServerRegistry

__all__ = ['MCPClient', 'MCPServerRegistry']

