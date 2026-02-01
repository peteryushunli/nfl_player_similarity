"""
Similarity-related API endpoints.

Endpoints:
- POST /find - Find players similar to a target player
"""

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_similarity_model
from src.api.schemas.similarity import SimilarityRequest, SimilarityResponse, SimilarPlayer
from src.api.schemas.player import PlayerInfo
from src.models.similarity_v2 import PlayerSimilarityModel

# Create the router
router = APIRouter()


@router.post("/find", response_model=SimilarityResponse)
def find_similar_players(
    request: SimilarityRequest,
    model: PlayerSimilarityModel = Depends(get_similarity_model)
):
    """
    Find players similar to the target player.

    This is the core functionality of the app. Given a player ID,
    it finds other players with similar career trajectories based on:
    - Statistical output (yards, touchdowns, etc.)
    - Fantasy point production
    - Draft capital (where they were drafted)

    The comparison can be done in two modes:
    - "season_number": Compare first N seasons (default, more intuitive)
    - "age": Compare at the same ages

    Example request body:
    {
        "gsis_id": "00-0033873",
        "mode": "season_number",
        "max_results": 15,
        "through_season": 5
    }
    """
    try:
        # Call the model's find_similar_players method
        result = model.find_similar_players(
            gsis_id=request.gsis_id,
            mode=request.mode,
            max_results=request.max_results,
            through_season=request.through_season
        )
    except ValueError as e:
        # ValueError is raised when player is not found
        raise HTTPException(status_code=404, detail=str(e))

    # Convert the target player to our schema
    target = result.target_player
    target_player = PlayerInfo(
        gsis_id=target.gsis_id,
        name=target.name,
        position=target.position,
        first_season=target.first_season,
        last_season=target.last_season,
        seasons_played=target.seasons_played,
        draft_year=int(target.draft_year) if target.draft_year else None,
        draft_round=int(target.draft_round) if target.draft_round else None,
        draft_pick=int(target.draft_pick) if target.draft_pick else None,
        draft_position_pick=int(target.draft_position_pick) if target.draft_position_pick else None
    )

    # Convert the similar players DataFrame to our schema
    similar_players = []
    for _, row in result.similar_players.iterrows():
        similar_players.append(
            SimilarPlayer(
                gsis_id=row["gsis_id"],
                name=row["name"],
                similarity_score=round(float(row["similarity_score"]), 4),
                euclidean_score=round(float(row["euclidean_score"]), 4) if "euclidean_score" in row and row["euclidean_score"] is not None else None,
                fantasy_score=round(float(row["fantasy_score"]), 4) if "fantasy_score" in row and row["fantasy_score"] is not None else None,
                draft_score=round(float(row["draft_score"]), 4) if "draft_score" in row and row["draft_score"] is not None else None
            )
        )

    return SimilarityResponse(
        target_player=target_player,
        similar_players=similar_players,
        comparison_mode=result.comparison_mode,
        comparison_range=result.comparison_range
    )
