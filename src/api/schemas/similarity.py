"""
Pydantic schemas for similarity-related API endpoints.

These schemas define the shape of data for:
- Similarity search requests
- Similar player results
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Tuple
from .player import PlayerInfo, AggregatedStats, SeasonStats


class CareerDataPoint(BaseModel):
    """A single data point for career trajectory chart."""
    season_number: int
    season: int  # actual year
    fantasy_points: float  # half PPR


class SimilarPlayer(BaseModel):
    """
    A single player from the similarity results.

    Contains the player's basic info plus their similarity scores.
    Lower similarity_score = more similar to the target player.
    """
    gsis_id: str
    name: str
    position: str
    first_season: int
    headshot_url: Optional[str] = None
    # Draft info for context
    draft_year: Optional[int] = None
    draft_round: Optional[int] = None
    draft_pick: Optional[int] = None
    draft_position_pick: Optional[int] = None  # e.g., 1st QB taken, 2nd RB taken
    # Main score - lower is more similar (0 = identical)
    similarity_score: float
    # Component scores for transparency
    euclidean_score: Optional[float] = None   # Statistical distance
    fantasy_score: Optional[float] = None      # Fantasy point similarity
    draft_score: Optional[float] = None        # Draft capital similarity (higher = more similar)
    # Aggregated stats for the comparison period
    stats: Optional[AggregatedStats] = None
    # Full career trajectory for chart (all seasons, not just comparison range)
    career_data: List[CareerDataPoint] = []


class SimilarityRequest(BaseModel):
    """
    Request body for finding similar players.

    Example:
        {
            "gsis_id": "00-0033873",  # Patrick Mahomes
            "mode": "season_number",
            "scoring_format": "half_ppr",
            "max_results": 15,
            "through_season": 5  # Compare first 5 seasons only
        }
    """
    gsis_id: str = Field(..., description="GSIS ID of the target player")
    mode: Literal["age", "season_number"] = Field(
        default="season_number",
        description="Comparison mode: 'season_number' compares first N seasons, 'age' compares at same ages"
    )
    scoring_format: Literal["standard", "half_ppr", "ppr"] = Field(
        default="half_ppr",
        description="Fantasy scoring format: 'standard' (0 PPR), 'half_ppr' (0.5 PPR), 'ppr' (1.0 PPR)"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum number of similar players to return"
    )
    through_season: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Compare through this season number (e.g., 3 = first 3 seasons). If null, uses all seasons."
    )


class SimilarityResponse(BaseModel):
    """
    Response from the similarity search.

    Contains the target player's info, the list of similar players,
    and metadata about how the comparison was done.
    """
    target_player: PlayerInfo
    target_stats: AggregatedStats  # Target player's aggregated stats for the comparison period
    target_seasons: List[SeasonStats]  # Target player's season-by-season stats
    target_career_data: List[CareerDataPoint] = []  # Full career trajectory for chart
    similar_players: List[SimilarPlayer]
    comparison_mode: str  # "age" or "season_number"
    scoring_format: str = "half_ppr"  # "standard", "half_ppr", or "ppr"
    # The range of ages or season numbers that were compared
    # e.g., (1, 5) means seasons 1 through 5
    comparison_range: Tuple[Optional[int], Optional[int]]
