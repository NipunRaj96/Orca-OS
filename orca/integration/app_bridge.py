"""
Application-level integration bridge for Orca OS.
"""

import logging
import json
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..database.session import DatabaseSession
from ..database.models import AppIntegration
from ..llm.manager import LLMManager

logger = logging.getLogger(__name__)


class AppBridge:
    """Bridge for integrating Orca AI with applications."""
    
    def __init__(self, db_session: DatabaseSession, llm_manager: LLMManager):
        """Initialize app bridge."""
        self.db = db_session
        self.llm_manager = llm_manager
        self.integrations = {}
        self._load_integrations()
    
    def _load_integrations(self):
        """Load registered application integrations."""
        with self.db.session() as session:
            integrations = session.query(AppIntegration).filter_by(enabled=True).all()
            for integration in integrations:
                self.integrations[integration.app_name] = integration
    
    def register_app(
        self,
        app_name: str,
        app_type: str,
        integration_type: str,
        config: Dict[str, Any]
    ):
        """Register an application integration."""
        with self.db.session() as session:
            existing = session.query(AppIntegration).filter_by(app_name=app_name).first()
            if existing:
                existing.app_type = app_type
                existing.integration_type = integration_type
                existing.config = config
                existing.enabled = True
            else:
                integration = AppIntegration(
                    app_name=app_name,
                    app_type=app_type,
                    integration_type=integration_type,
                    config=config,
                    enabled=True
                )
                session.add(integration)
            session.commit()
        
        self._load_integrations()
    
    def get_app_context(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get context from an application."""
        integration = self.integrations.get(app_name)
        if not integration:
            return None
        
        # Different methods based on integration type
        if integration.integration_type == 'bridge':
            return self._get_bridge_context(app_name, integration.config)
        elif integration.integration_type == 'plugin':
            return self._get_plugin_context(app_name, integration.config)
        elif integration.integration_type == 'api':
            return self._get_api_context(app_name, integration.config)
        
        return None
    
    def _get_bridge_context(self, app_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get context via bridge integration."""
        # Bridge integrations use IPC or file-based communication
        bridge_path = config.get('bridge_path')
        if bridge_path and Path(bridge_path).exists():
            try:
                with open(bridge_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading bridge context: {e}")
        return {}
    
    def _get_plugin_context(self, app_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get context via plugin integration."""
        # Plugin integrations use plugin system
        plugin_name = config.get('plugin_name')
        if plugin_name:
            # Call plugin to get context
            return {'plugin': plugin_name, 'context': 'available'}
        return {}
    
    def _get_api_context(self, app_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get context via API integration."""
        # API integrations use HTTP/WebSocket
        api_url = config.get('api_url')
        if api_url:
            # Make API call (placeholder)
            return {'api': api_url, 'context': 'available'}
        return {}
    
    async def process_app_query(
        self,
        app_name: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a query in the context of an application."""
        # Get app context
        app_context = self.get_app_context(app_name) or {}
        
        # Merge with provided context
        full_context = {**app_context, **(context or {})}
        
        # Use LLM to process query with app context
        from ..core.models import UserQuery, SystemContext
        user_query = UserQuery(query=query)
        system_context = SystemContext()
        
        # Add app context to system context
        system_context.context = full_context
        
        suggestion = await self.llm_manager.generate_suggestion(user_query, system_context)
        
        return {
            'app': app_name,
            'suggestion': suggestion.dict() if hasattr(suggestion, 'dict') else str(suggestion),
            'context_used': full_context
        }


class AppIntegrationManager:
    """Manages application integrations."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize integration manager."""
        self.db = db_session
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all registered integrations."""
        with self.db.session() as session:
            integrations = session.query(AppIntegration).all()
            return [
                {
                    'app_name': i.app_name,
                    'app_type': i.app_type,
                    'integration_type': i.integration_type,
                    'enabled': i.enabled,
                    'last_used': i.last_used.isoformat() if i.last_used else None
                }
                for i in integrations
            ]
    
    def enable_integration(self, app_name: str):
        """Enable an integration."""
        with self.db.session() as session:
            integration = session.query(AppIntegration).filter_by(app_name=app_name).first()
            if integration:
                integration.enabled = True
                session.commit()
    
    def disable_integration(self, app_name: str):
        """Disable an integration."""
        with self.db.session() as session:
            integration = session.query(AppIntegration).filter_by(app_name=app_name).first()
            if integration:
                integration.enabled = False
                session.commit()

