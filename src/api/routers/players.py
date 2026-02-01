"""
Player-related API endpoints.

Endpoints:
- GET /search - Search for players by name
- GET /{gsis_id} - Get detailed player information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from src.api.dependencies import get_similarity_model
from src.api.schemas.player import PlayerSearchResponse, PlayerInfo, PlayerSummary
from src.models.similarity_v2 import PlayerSimilarityModel

# Create the router - this groups all player-related endpoints
router = APIRouter()


@router.get("/search", response_model=PlayerSearchResponse)
def search_players(
    q: str = Query(
        ...,  # ... means required
        min_length=2,
        description="Search query (player name). Minimum 2 characters."
    ),
    position: Optional[str] = Query(
        None,
        pattern="^(QB|RB|WR|TE)$",  # Only allow valid positions
        description="Filter by position (optional): QB, RB, WR, or TE"
    ),
    model: PlayerSimilarityModel = Depends(get_similarity_model)
):
    """
    Search for players by name.

    Returns a list of players matching the search query.
    Optionally filter by position.

    Examples:
    - /search?q=mahomes -> Returns Patrick Mahomes and any other "mahomes"
    - /search?q=henry&position=RB -> Returns Derrick Henry (RB), not Hunter Henry (TE)
    """
    # Call the model's search method
    results_df = model.search_players(q, position=position)

    # Convert DataFrame rows to Pydantic models
    players = [
        PlayerSummary(
            gsis_id=row["gsis_id"],
            name=row["name"],
            position=row["position"],
            first_season=int(row["first_season"]),
            last_season=int(row["last_season"]),
            seasons_played=int(row["seasons_played"])
        )
        for _, row in results_df.iterrows()
    ]

    return PlayerSearchResponse(players=players)


@router.get("/{gsis_id}", response_model=PlayerInfo)
def get_player(
    gsis_id: str,
    model: PlayerSimilarityModel = Depends(get_similarity_model)
):
    """
    Get detailed information about a specific player.

    Returns full player info including draft data.
    Returns 404 if the player is not found.

    The gsis_id is the NFL's unique identifier for players.
    Example: 00-0033873 is Patrick Mahomes
    """
    # Get player info from the model
    player_info = model.get_player_info(gsis_id)

    # Return 404 if player not found
    if player_info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Player not found: {gsis_id}"
        )

    # Convert to Pydantic model
    # We need to handle Optional fields that might be float (from pandas)
    return PlayerInfo(
        gsis_id=player_info.gsis_id,
        name=player_info.name,
        position=player_info.position,
        first_season=player_info.first_season,
        last_season=player_info.last_season,
        seasons_played=player_info.seasons_played,
        draft_year=int(player_info.draft_year) if player_info.draft_year else None,
        draft_round=int(player_info.draft_round) if player_info.draft_round else None,
        draft_pick=int(player_info.draft_pick) if player_info.draft_pick else None,
        draft_position_pick=int(player_info.draft_position_pick) if player_info.draft_position_pick else None
    )
