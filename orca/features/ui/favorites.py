"""
Favorites system for Orca OS.
Save and quickly execute frequently used commands.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from ...database.session import DatabaseSession
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)
console = Console()


class FavoritesManager:
    """Manages favorite commands for Orca OS."""
    
    def __init__(self):
        """Initialize favorites manager."""
        initialize_database()
        self.db = DatabaseSession()
        self._init_favorites_table()
    
    def _init_favorites_table(self):
        """Initialize favorites table if it doesn't exist."""
        from ...database.models import Base
        from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
        
        # Check if table exists, create if not
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                # Try to query favorites table
                session.execute(text("SELECT 1 FROM favorites LIMIT 1"))
        except Exception:
            # Create table
            class Favorite(Base):
                __tablename__ = 'favorites'
                
                id = Column(Integer, primary_key=True)
                user_id = Column(String(255), default="default", index=True)
                name = Column(String(255), nullable=False)
                query = Column(Text, nullable=False)
                category = Column(String(100))
                description = Column(Text)
                created_at = Column(DateTime, default=datetime.now)
                last_used = Column(DateTime)
                use_count = Column(Integer, default=0)
            
            from ...database.models import get_engine
            engine = get_engine()
            Base.metadata.create_all(engine)
    
    def list_favorites(self, user_id: str = "default", category: Optional[str] = None):
        """List all favorites."""
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                # Simple query using raw SQL for now
                query = "SELECT id, name, query, category, description, use_count FROM favorites WHERE user_id = :user_id"
                params = {"user_id": user_id}
                
                if category:
                    query += " AND category = :category"
                    params["category"] = category
                
                query += " ORDER BY use_count DESC, name"
                
                result = session.execute(text(query), params)
                favorites = result.fetchall()
                
                if not favorites:
                    console.print("[yellow]No favorites saved yet[/yellow]")
                    console.print("[dim]Use 'orca --favorite-add' to add favorites[/dim]")
                    return
                
                table = Table(title="Favorites", box=box.ROUNDED)
                table.add_column("#", style="cyan", width=4)
                table.add_column("Name", style="white", width=20)
                table.add_column("Query", style="green", width=40)
                table.add_column("Category", style="yellow", width=15)
                table.add_column("Used", style="dim", width=8)
                
                for fav in favorites:
                    query_text = fav[2][:37] + "..." if len(fav[2]) > 40 else fav[2]
                    table.add_row(
                        str(fav[0]),
                        fav[1],
                        query_text,
                        fav[3] or "default",
                        str(fav[5] or 0)
                    )
                
                console.print(table)
        except Exception as e:
            logger.error(f"Error listing favorites: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    def add_favorite(self, name: str, query: str, category: Optional[str] = None, 
                     description: Optional[str] = None, user_id: str = "default"):
        """Add a favorite command."""
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                # Check if name already exists
                check = session.execute(
                    text("SELECT id FROM favorites WHERE user_id = :user_id AND name = :name"),
                    {"user_id": user_id, "name": name}
                ).fetchone()
                
                if check:
                    if not Confirm.ask(f"[yellow]Favorite '{name}' already exists. Overwrite?[/yellow]"):
                        console.print("[yellow]Cancelled[/yellow]")
                        return
                    # Update existing
                    session.execute(
                        text("UPDATE favorites SET query = :query, category = :category, description = :description WHERE id = :id"),
                        {"query": query, "category": category, "description": description, "id": check[0]}
                    )
                    console.print(f"[green]✅ Updated favorite '{name}'[/green]")
                else:
                    # Insert new
                    session.execute(
                        text("INSERT INTO favorites (user_id, name, query, category, description, created_at, use_count) VALUES (:user_id, :name, :query, :category, :description, :created_at, :use_count)"),
                        {"user_id": user_id, "name": name, "query": query, "category": category, "description": description, "created_at": datetime.now(), "use_count": 0}
                    )
                    console.print(f"[green]✅ Added favorite '{name}'[/green]")
                
                session.commit()
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    def remove_favorite(self, name: str, user_id: str = "default"):
        """Remove a favorite."""
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                result = session.execute(
                    text("DELETE FROM favorites WHERE user_id = :user_id AND name = :name"),
                    {"user_id": user_id, "name": name}
                )
                
                if result.rowcount > 0:
                    session.commit()
                    console.print(f"[green]✅ Removed favorite '{name}'[/green]")
                else:
                    console.print(f"[yellow]Favorite '{name}' not found[/yellow]")
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    def get_favorite(self, name: str, user_id: str = "default") -> Optional[str]:
        """Get favorite query by name."""
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                result = session.execute(
                    text("SELECT query FROM favorites WHERE user_id = :user_id AND name = :name"),
                    {"user_id": user_id, "name": name}
                ).fetchone()
                
                if result:
                    # Update use count and last used
                    session.execute(
                        text("UPDATE favorites SET use_count = use_count + 1, last_used = :last_used WHERE user_id = :user_id AND name = :name"),
                        {"last_used": datetime.now(), "user_id": user_id, "name": name}
                    )
                    session.commit()
                    return result[0]
                return None
        except Exception as e:
            logger.error(f"Error getting favorite: {e}")
            return None
    
    def show_categories(self, user_id: str = "default"):
        """Show all favorite categories."""
        try:
            from sqlalchemy import text
            with self.db.session() as session:
                result = session.execute(
                    text("SELECT DISTINCT category, COUNT(*) as count FROM favorites WHERE user_id = :user_id GROUP BY category"),
                    {"user_id": user_id}
                ).fetchall()
                
                if not result:
                    console.print("[yellow]No categories found[/yellow]")
                    return
                
                table = Table(title="Favorite Categories", box=box.ROUNDED)
                table.add_column("Category", style="cyan", width=20)
                table.add_column("Count", style="green", width=10)
                
                for row in result:
                    category = row[0] or "default"
                    table.add_row(category, str(row[1]))
                
                console.print(table)
        except Exception as e:
            logger.error(f"Error showing categories: {e}")
            console.print(f"[red]Error: {e}[/red]")

