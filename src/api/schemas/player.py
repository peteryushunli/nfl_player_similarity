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


class StatPercentiles(BaseModel):
    """Percentile rankings for stats (0-100, higher = better) within position for that season."""
    games_played: Optional[int] = None
    pass_yards: Optional[int] = None
    pass_tds: Optional[int] = None
    rush_yards: Optional[int] = None
    rush_tds: Optional[int] = None
    receptions: Optional[int] = None
    receiving_yards: Optional[int] = None
    receiving_tds: Optional[int] = None
    fantasy_points: Optional[int] = None


class SeasonStats(BaseModel):
    """Stats for a single season."""
    season: int
    season_number: int
    age: Optional[int] = None
    games_played: int = 0
    games_started: int = 0
    # Passing
    pass_completions: int = 0
    pass_attempts: int = 0
    pass_yards: int = 0
    pass_tds: int = 0
    interceptions: int = 0
    # Rushing
    rush_attempts: int = 0
    rush_yards: int = 0
    rush_tds: int = 0
    # Receiving
    targets: int = 0
    receptions: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0
    # Fantasy (half PPR)
    fantasy_points: float = 0.0
    # Rankings (based on half PPR)
    fantasy_position_rank: Optional[int] = None
    fantasy_overall_rank: Optional[int] = None
    # Percentiles for heatmap (within position for that season)
    percentiles: Optional[StatPercentiles] = None


class AggregatedStats(BaseModel):
    """Aggregated stats across multiple seasons for comparison."""
    seasons_included: List[int]
    games_played: int = 0
    games_started: int = 0
    # Passing totals
    pass_completions: int = 0
    pass_attempts: int = 0
    pass_yards: int = 0
    pass_tds: int = 0
    interceptions: int = 0
    # Rushing totals
    rush_attempts: int = 0
    rush_yards: int = 0
    rush_tds: int = 0
    # Receiving totals
    targets: int = 0
    receptions: int = 0
    receiving_yards: int = 0
    receiving_tds: int = 0
    # Fantasy totals (half PPR)
    fantasy_points: float = 0.0


class PlayerWithStats(PlayerInfo):
    """Player info with season-by-season stats."""
    seasons: List[SeasonStats] = []
