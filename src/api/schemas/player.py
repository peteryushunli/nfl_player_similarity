"""
Pydantic schemas for player-related API endpoints.

These schemas define the shape of data for:
- Player search results
- Detailed player information
"""

from pydantic import BaseModel
from typing import Optional, List


class PlayerSummary(BaseModel):
    """
    Basic player information returned in search results.

    This is a lighter version of PlayerInfo, used when listing
    multiple players (e.g., search results).
    """
    gsis_id: str
    name: str
    position: str
    first_season: int
    last_season: int
    seasons_played: int


class PlayerInfo(BaseModel):
    """
    Detailed player information including draft data.

    Used when displaying a single player's full profile.
    """
    gsis_id: str
    name: str
    position: str
    first_season: int
    last_season: int
    seasons_played: int
    # Draft info is optional - not all players were drafted (UDFAs)
    # or we might not have draft data for older players
    draft_year: Optional[int] = None
    draft_round: Optional[int] = None
    draft_pick: Optional[int] = None
    draft_position_pick: Optional[int] = None


class PlayerSearchResponse(BaseModel):
    """Response wrapper for player search endpoint."""
    players: List[PlayerSummary]
