"""
MCP Server Registry for managing multiple MCP connections.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .client import MCPClient, GmailMCPClient

logger = logging.getLogger(__name__)


class MCPServerRegistry:
    """Registry for managing MCP server connections."""
    
    def __init__(self):
        """Initialize server registry."""
        self.servers: Dict[str, MCPClient] = {}
        self.config_path = Path.home() / ".orca" / "mcp_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load MCP server configurations."""
        if self.config_path.exists():
            try:
                import json
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load MCP config: {e}")
                self.config = {}
        else:
            self.config = {}
    
    def register_server(self, name: str, server_type: str, config: Dict[str, Any]) -> bool:
        """
        Register an MCP server.
        
        Args:
            name: Server name/identifier
            server_type: Type of server (gmail, slack, etc.)
            config: Server configuration
        
        Returns:
            True if registration successful
        """
        try:
            if server_type == "gmail":
                client = GmailMCPClient()
                if client.connect(config.get("credentials_path")):
                    self.servers[name] = client
                    self.config[name] = {
                        "type": server_type,
                        "config": config
                    }
                    self._save_config()
                    return True
            else:
                logger.error(f"Unknown server type: {server_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to register server {name}: {e}")
            return False
    
    def get_server(self, name: str) -> Optional[MCPClient]:
        """
        Get a registered MCP server.
        
        Args:
            name: Server name
        
        Returns:
            MCPClient instance or None
        """
        return self.servers.get(name)
    
    def list_servers(self) -> List[str]:
        """List all registered servers."""
        return list(self.servers.keys())
    
    def _save_config(self):
        """Save MCP server configurations."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save MCP config: {e}")

