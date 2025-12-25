"""
Database session management for Orca OS.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from .models import get_db, get_session_factory


class DatabaseSession:
    """Database session manager."""
    
    def __init__(self):
        self.factory = get_session_factory()
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get database session context manager."""
        db = self.factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_session(self) -> Session:
        """Get database session (manual management)."""
        return self.factory()

