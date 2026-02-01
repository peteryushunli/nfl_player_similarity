"""
Shared dependencies for FastAPI endpoints.

This module provides dependency injection for:
- Database connections
- The similarity model

Using dependency injection makes the code:
- Easier to test (can mock dependencies)
- More maintainable (single source of truth for shared resources)
"""

from functools import lru_cache
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.db.database import Database, get_database
from src.models.similarity_v2 import PlayerSimilarityModel


def get_db() -> Database:
    """
    Get a database connection.

    Returns:
        Database instance
    """
    return get_database()


@lru_cache()
def get_similarity_model() -> PlayerSimilarityModel:
    """
    Get the similarity model instance (cached/singleton).

    The @lru_cache decorator ensures we only create one instance
    of the model, which then gets reused for all requests.
    This is important because the model loads data from the database
    on initialization, so we don't want to do that for every request.

    Returns:
        PlayerSimilarityModel instance
    """
    db = get_database()
    return PlayerSimilarityModel(db)
