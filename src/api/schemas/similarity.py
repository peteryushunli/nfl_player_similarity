"""
Pydantic schemas for similarity-related API endpoints.

These schemas define the shape of data for:
- Similarity search requests
- Similar player results
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Tuple
from .player import PlayerInfo


class SimilarPlayer(BaseModel):
    """
    A single player from the similarity results.

    Contains the player's basic info plus their similarity scores.
    Lower similarity_score = more similar to the target player.
    """
    gsis_id: str
    name: str
    # Main score - lower is more similar (0 = identical)
    similarity_score: float
    # Component scores for transparency
    euclidean_score: Optional[float] = None   # Statistical distance
    fantasy_score: Optional[float] = None      # Fantasy point similarity
    draft_score: Optional[float] = None        # Draft capital similarity (higher = more similar)


class SimilarityRequest(BaseModel):
    """
    Request body for finding similar players.

    Example:
        {
            "gsis_id": "00-0033873",  # Patrick Mahomes
            "mode": "season_number",
            "max_results": 15,
            "through_season": 5  # Compare first 5 seasons only
        }
    """
    gsis_id: str = Field(..., description="GSIS ID of the target player")
    mode: Literal["age", "season_number"] = Field(
        default="season_number",
        description="Comparison mode: 'season_number' compares first N seasons, 'age' compares at same ages"
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
    similar_players: List[SimilarPlayer]
    comparison_mode: str  # "age" or "season_number"
    # The range of ages or season numbers that were compared
    # e.g., (1, 5) means seasons 1 through 5
    comparison_range: Tuple[Optional[int], Optional[int]]
