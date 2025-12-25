"""
Initialize Orca OS database.
"""

from .models import init_db, get_db_path
import logging

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database (create tables)."""
    try:
        db_path = get_db_path()
        logger.info(f"Initializing database at: {db_path}")
        engine = init_db()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


if __name__ == "__main__":
    initialize_database()

