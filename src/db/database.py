"""
Database connection and initialization for NFL Player Similarity.

Uses SQLite for local development. Can be migrated to PostgreSQL for production.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default database location
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "nfl_similarity.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Database:
    """SQLite database wrapper for NFL Player Similarity."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to data/nfl_similarity.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection with row factory set to sqlite3.Row
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def initialize(self, force: bool = False) -> None:
        """
        Initialize the database schema.

        Args:
            force: If True, drop and recreate all tables. USE WITH CAUTION.
        """
        if force and self.db_path.exists():
            logger.warning(f"Force flag set. Removing existing database at {self.db_path}")
            self.db_path.unlink()

        with self.get_connection() as conn:
            # Read and execute schema
            schema_sql = SCHEMA_PATH.read_text()
            conn.executescript(schema_sql)
            logger.info(f"Database initialized at {self.db_path}")

    def is_initialized(self) -> bool:
        """Check if the database has been initialized with the schema."""
        if not self.db_path.exists():
            return False

        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='players'"
            )
            return cursor.fetchone() is not None

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {}

            # Count players
            cursor = conn.execute("SELECT COUNT(*) FROM players")
            stats["total_players"] = cursor.fetchone()[0]

            # Count by position
            cursor = conn.execute(
                "SELECT position, COUNT(*) FROM players GROUP BY position"
            )
            stats["players_by_position"] = dict(cursor.fetchall())

            # Count seasons
            cursor = conn.execute("SELECT COUNT(*) FROM seasons")
            stats["total_season_records"] = cursor.fetchone()[0]

            # Season range
            cursor = conn.execute("SELECT MIN(season), MAX(season) FROM seasons")
            row = cursor.fetchone()
            stats["season_range"] = (row[0], row[1]) if row[0] else (None, None)

            # Draft records
            cursor = conn.execute("SELECT COUNT(*) FROM draft")
            stats["draft_records"] = cursor.fetchone()[0]

            return stats

    def clear_data(self) -> None:
        """Clear all data from tables (keeps schema intact)."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM seasons")
            conn.execute("DELETE FROM draft")
            conn.execute("DELETE FROM players")
            logger.info("All data cleared from database")


# Singleton instance for convenience
_db_instance: Optional[Database] = None


def get_database(db_path: Optional[Path] = None) -> Database:
    """
    Get the database instance (singleton pattern).

    Args:
        db_path: Optional path to database. Only used on first call.

    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
