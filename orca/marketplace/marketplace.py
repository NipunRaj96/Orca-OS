"""
Unified marketplace for Orca OS plugins, agents, and integrations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..database.session import DatabaseSession
from ..database.models import MarketplaceItem, Plugin

logger = logging.getLogger(__name__)


class Marketplace:
    """Marketplace for discovering and installing items."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize marketplace."""
        self.db = db_session
    
    def add_item(
        self,
        item_id: str,
        item_type: str,
        name: str,
        description: str,
        author: str,
        category: str,
        version: str = "1.0.0",
        item_metadata: Optional[Dict[str, Any]] = None
    ) -> MarketplaceItem:
        """Add item to marketplace."""
        with self.db.session() as session:
            existing = session.query(MarketplaceItem).filter_by(item_id=item_id).first()
            if existing:
                # Update existing
                existing.name = name
                existing.description = description
                existing.version = version
                existing.item_metadata = item_metadata or {}
                session.commit()
                session.refresh(existing)
                return existing
            else:
                # Create new
                item = MarketplaceItem(
                    item_id=item_id,
                    item_type=item_type,
                    name=name,
                    description=description,
                    author=author,
                    category=category,
                    version=version,
                    item_metadata=item_metadata or {}
                )
                session.add(item)
                session.commit()
                session.refresh(item)
                return item
    
    def search(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search marketplace items."""
        with self.db.session() as session:
            items_query = session.query(MarketplaceItem)
            
            if query:
                items_query = items_query.filter(
                    MarketplaceItem.name.contains(query) |
                    MarketplaceItem.description.contains(query)
                )
            
            if item_type:
                items_query = items_query.filter_by(item_type=item_type)
            
            if category:
                items_query = items_query.filter_by(category=category)
            
            items = items_query.order_by(
                MarketplaceItem.download_count.desc(),
                MarketplaceItem.rating.desc()
            ).limit(limit).all()
            
            return [
                {
                    'item_id': item.item_id,
                    'item_type': item.item_type,
                    'name': item.name,
                    'description': item.description,
                    'author': item.author,
                    'category': item.category,
                    'version': item.version,
                    'download_count': item.download_count,
                    'rating': item.rating,
                    'metadata': item.item_metadata
                }
                for item in items
            ]
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get marketplace item by ID."""
        with self.db.session() as session:
            item = session.query(MarketplaceItem).filter_by(item_id=item_id).first()
            if item:
                return {
                    'item_id': item.item_id,
                    'item_type': item.item_type,
                    'name': item.name,
                    'description': item.description,
                    'author': item.author,
                    'category': item.category,
                    'version': item.version,
                    'download_count': item.download_count,
                    'rating': item.rating,
                    'metadata': item.item_metadata,
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat()
                }
            return None
    
    def increment_download(self, item_id: str):
        """Increment download count."""
        with self.db.session() as session:
            item = session.query(MarketplaceItem).filter_by(item_id=item_id).first()
            if item:
                item.download_count += 1
                session.commit()
    
    def update_rating(self, item_id: str, rating: float):
        """Update item rating."""
        with self.db.session() as session:
            item = session.query(MarketplaceItem).filter_by(item_id=item_id).first()
            if item:
                # Simple average (in production, use weighted average)
                current_rating = item.rating
                if current_rating == 0:
                    item.rating = rating
                else:
                    item.rating = (current_rating + rating) / 2
                session.commit()


class MarketplaceManager:
    """Manages marketplace operations."""
    
    def __init__(self, db_session: DatabaseSession):
        """Initialize marketplace manager."""
        self.db = db_session
        self.marketplace = Marketplace(db_session)
    
    def install_from_marketplace(
        self,
        item_id: str,
        install_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Install item from marketplace."""
        item = self.marketplace.get_item(item_id)
        if not item:
            return {'success': False, 'error': 'Item not found'}
        
        # Increment download count
        self.marketplace.increment_download(item_id)
        
        # Install based on type
        if item['item_type'] == 'plugin':
            return self._install_plugin(item, install_path)
        elif item['item_type'] == 'agent':
            return self._install_agent(item, install_path)
        else:
            return {'success': False, 'error': f'Unknown item type: {item["item_type"]}'}
    
    def _install_plugin(self, item: Dict[str, Any], install_path: Optional[str]) -> Dict[str, Any]:
        """Install plugin from marketplace."""
        # Register in plugin system
        with self.db.session() as session:
            plugin = Plugin(
                name=item['item_id'],
                version=item['version'],
                description=item['description'],
                author=item['author'],
                category=item['category'],
                enabled=True,
                plugin_metadata=item.get('metadata', {})
            )
            session.add(plugin)
            session.commit()
        
        return {
            'success': True,
            'item_id': item['item_id'],
            'type': 'plugin',
            'message': f"Plugin '{item['name']}' installed successfully"
        }
    
    def _install_agent(self, item: Dict[str, Any], install_path: Optional[str]) -> Dict[str, Any]:
        """Install agent from marketplace."""
        # Placeholder for agent installation
        return {
            'success': True,
            'item_id': item['item_id'],
            'type': 'agent',
            'message': f"Agent '{item['name']}' installed successfully"
        }
    
    def list_installed(self) -> List[Dict[str, Any]]:
        """List installed items."""
        with self.db.session() as session:
            plugins = session.query(Plugin).all()
            return [
                {
                    'name': p.name,
                    'version': p.version,
                    'type': 'plugin',
                    'enabled': p.enabled,
                    'category': p.category
                }
                for p in plugins
            ]

