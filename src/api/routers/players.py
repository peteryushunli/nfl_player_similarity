"""
Player-related API endpoints.

Endpoints:
- GET /search - Search for players by name
- GET /{gsis_id} - Get detailed player information
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from src.api.dependencies import get_similarity_model, get_db
from src.api.schemas.player import PlayerSearchResponse, PlayerInfo, PlayerSummary, SeasonStats, PlayerWithStats
from src.models.similarity_v2 import PlayerSimilarityModel
from src.db.database import Database

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
            seasons_played=int(row["seasons_played"]),
            headshot_url=row.get("headshot_url")
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
        headshot_url=player_info.headshot_url,
        draft_year=int(player_info.draft_year) if player_info.draft_year else None,
        draft_round=int(player_info.draft_round) if player_info.draft_round else None,
        draft_pick=int(player_info.draft_pick) if player_info.draft_pick else None,
        draft_position_pick=int(player_info.draft_position_pick) if player_info.draft_position_pick else None
    )


@router.get("/{gsis_id}/seasons", response_model=PlayerWithStats)
def get_player_seasons(
    gsis_id: str,
    model: PlayerSimilarityModel = Depends(get_similarity_model),
    db: Database = Depends(get_db)
):
    """
    Get a player's season-by-season stats.

    Returns player info plus all their seasonal stats in chronological order.
    """
    # Get player info
    player_info = model.get_player_info(gsis_id)
    if player_info is None:
        raise HTTPException(status_code=404, detail=f"Player not found: {gsis_id}")

    # Get season-by-season stats
    query = """
        SELECT
            season,
            season_number,
            team,
            games_played,
            games_started,
            pass_completions,
            pass_attempts,
            pass_yards,
            pass_tds,
            interceptions,
            rush_attempts,
            rush_yards,
            rush_tds,
            targets,
            receptions,
            receiving_yards,
            receiving_tds,
            fantasy_points_ppr,
            fantasy_points_half_ppr
        FROM seasons
        WHERE gsis_id = ?
        ORDER BY season ASC
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query, [gsis_id])
        rows = cursor.fetchall()

    seasons = [
        SeasonStats(
            season=row["season"],
            season_number=row["season_number"] or 0,
            team=row["team"],
            games_played=row["games_played"] or 0,
            games_started=row["games_started"] or 0,
            pass_completions=row["pass_completions"] or 0,
            pass_attempts=row["pass_attempts"] or 0,
            pass_yards=row["pass_yards"] or 0,
            pass_tds=row["pass_tds"] or 0,
            interceptions=row["interceptions"] or 0,
            rush_attempts=row["rush_attempts"] or 0,
            rush_yards=row["rush_yards"] or 0,
            rush_tds=row["rush_tds"] or 0,
            targets=row["targets"] or 0,
            receptions=row["receptions"] or 0,
            receiving_yards=row["receiving_yards"] or 0,
            receiving_tds=row["receiving_tds"] or 0,
            fantasy_points_ppr=float(row["fantasy_points_ppr"] or 0),
            fantasy_points_half_ppr=float(row["fantasy_points_half_ppr"] or 0),
        )
        for row in rows
    ]

    return PlayerWithStats(
        gsis_id=player_info.gsis_id,
        name=player_info.name,
        position=player_info.position,
        first_season=player_info.first_season,
        last_season=player_info.last_season,
        seasons_played=player_info.seasons_played,
        draft_year=int(player_info.draft_year) if player_info.draft_year else None,
        draft_round=int(player_info.draft_round) if player_info.draft_round else None,
        draft_pick=int(player_info.draft_pick) if player_info.draft_pick else None,
        draft_position_pick=int(player_info.draft_position_pick) if player_info.draft_position_pick else None,
        seasons=seasons
    )
