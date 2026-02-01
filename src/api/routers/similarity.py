"""
Similarity-related API endpoints.

Endpoints:
- POST /find - Find players similar to a target player
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_similarity_model, get_db
from src.api.schemas.similarity import SimilarityRequest, SimilarityResponse, SimilarPlayer
from src.api.schemas.player import PlayerInfo, AggregatedStats, SeasonStats, StatPercentiles
from src.models.similarity_v2 import PlayerSimilarityModel
from src.db.database import Database

# Create the router
router = APIRouter()


def calc_half_ppr(ppr_points: float, receptions: int) -> float:
    """Calculate half PPR from full PPR by subtracting 0.5 per reception."""
    return round(ppr_points - (0.5 * receptions), 1)


def get_aggregated_stats(
    db: Database,
    gsis_id: str,
    season_numbers: List[int],
    mode: str = "season_number"
) -> AggregatedStats:
    """
    Get aggregated stats for a player over specified seasons.

    Args:
        db: Database connection
        gsis_id: Player's GSIS ID
        season_numbers: List of season numbers (1, 2, 3, etc.) to aggregate
        mode: "season_number" or "age" (affects which column to filter on)

    Returns:
        AggregatedStats with totals for all specified seasons
    """
    if mode == "season_number":
        filter_col = "season_number"
    else:
        filter_col = "age"

    placeholders = ",".join("?" * len(season_numbers))
    query = f"""
        SELECT
            GROUP_CONCAT(season) as seasons,
            SUM(games_played) as games_played,
            SUM(games_started) as games_started,
            SUM(pass_completions) as pass_completions,
            SUM(pass_attempts) as pass_attempts,
            SUM(pass_yards) as pass_yards,
            SUM(pass_tds) as pass_tds,
            SUM(interceptions) as interceptions,
            SUM(rush_attempts) as rush_attempts,
            SUM(rush_yards) as rush_yards,
            SUM(rush_tds) as rush_tds,
            SUM(targets) as targets,
            SUM(receptions) as receptions,
            SUM(receiving_yards) as receiving_yards,
            SUM(receiving_tds) as receiving_tds,
            SUM(fantasy_points_ppr) as fantasy_points_ppr
        FROM seasons
        WHERE gsis_id = ? AND {filter_col} IN ({placeholders})
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query, [gsis_id] + season_numbers)
        row = cursor.fetchone()

    if not row or row["seasons"] is None:
        return AggregatedStats(seasons_included=[])

    seasons_list = [int(s) for s in row["seasons"].split(",")] if row["seasons"] else []
    receptions = int(row["receptions"] or 0)
    ppr_points = float(row["fantasy_points_ppr"] or 0)

    return AggregatedStats(
        seasons_included=sorted(seasons_list),
        games_played=int(row["games_played"] or 0),
        games_started=int(row["games_started"] or 0),
        pass_completions=int(row["pass_completions"] or 0),
        pass_attempts=int(row["pass_attempts"] or 0),
        pass_yards=int(row["pass_yards"] or 0),
        pass_tds=int(row["pass_tds"] or 0),
        interceptions=int(row["interceptions"] or 0),
        rush_attempts=int(row["rush_attempts"] or 0),
        rush_yards=int(row["rush_yards"] or 0),
        rush_tds=int(row["rush_tds"] or 0),
        targets=int(row["targets"] or 0),
        receptions=receptions,
        receiving_yards=int(row["receiving_yards"] or 0),
        receiving_tds=int(row["receiving_tds"] or 0),
        fantasy_points=calc_half_ppr(ppr_points, receptions),
    )


def get_player_seasons(db: Database, gsis_id: str, season_numbers: List[int], mode: str = "season_number") -> List[SeasonStats]:
    """Get season-by-season stats for a player within the comparison range."""
    if mode == "season_number":
        filter_col = "season_number"
    else:
        filter_col = "age"

    placeholders = ",".join("?" * len(season_numbers))

    # Get player's birth year and position
    player_query = "SELECT birth_date, position FROM players WHERE gsis_id = ?"
    with db.get_connection() as conn:
        cursor = conn.execute(player_query, [gsis_id])
        player_row = cursor.fetchone()

    birth_year = None
    position = None
    if player_row:
        position = player_row["position"]
        if player_row["birth_date"]:
            try:
                birth_year = int(player_row["birth_date"][:4])
            except (ValueError, TypeError):
                pass

    # Get season stats
    query = f"""
        SELECT
            s.season,
            s.season_number,
            s.games_played,
            s.games_started,
            s.pass_completions,
            s.pass_attempts,
            s.pass_yards,
            s.pass_tds,
            s.interceptions,
            s.rush_attempts,
            s.rush_yards,
            s.rush_tds,
            s.targets,
            s.receptions,
            s.receiving_yards,
            s.receiving_tds,
            s.fantasy_points_ppr
        FROM seasons s
        WHERE s.gsis_id = ? AND s.{filter_col} IN ({placeholders})
        ORDER BY s.season ASC
    """

    with db.get_connection() as conn:
        cursor = conn.execute(query, [gsis_id] + season_numbers)
        rows = cursor.fetchall()

    result = []
    for row in rows:
        season_year = row["season"]
        receptions = row["receptions"] or 0
        ppr_points = float(row["fantasy_points_ppr"] or 0)
        half_ppr = calc_half_ppr(ppr_points, receptions)

        # Calculate age
        age = None
        if birth_year:
            age = season_year - birth_year

        # Calculate overall rank (by half PPR among all skill position players)
        overall_rank_query = """
            SELECT COUNT(*) + 1 as rank
            FROM seasons s
            JOIN players p ON s.gsis_id = p.gsis_id
            WHERE s.season = ?
              AND p.position IN ('QB', 'RB', 'WR', 'TE')
              AND (s.fantasy_points_ppr - 0.5 * s.receptions) > ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(overall_rank_query, [season_year, half_ppr])
            rank_row = cursor.fetchone()
            overall_rank = rank_row["rank"] if rank_row else None

        # Calculate position rank (by half PPR among same position)
        pos_rank_query = """
            SELECT COUNT(*) + 1 as rank
            FROM seasons s
            JOIN players p ON s.gsis_id = p.gsis_id
            WHERE s.season = ?
              AND p.position = ?
              AND (s.fantasy_points_ppr - 0.5 * s.receptions) > ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(pos_rank_query, [season_year, position, half_ppr])
            rank_row = cursor.fetchone()
            pos_rank = rank_row["rank"] if rank_row else None

        # Calculate percentiles within position for that season
        percentiles = None
        if position:
            percentiles = calculate_percentiles(db, season_year, position, row)

        result.append(SeasonStats(
            season=row["season"],
            season_number=row["season_number"] or 0,
            age=age,
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
            receptions=receptions,
            receiving_yards=row["receiving_yards"] or 0,
            receiving_tds=row["receiving_tds"] or 0,
            fantasy_points=half_ppr,
            fantasy_position_rank=pos_rank,
            fantasy_overall_rank=overall_rank,
            percentiles=percentiles,
        ))

    return result


def calculate_percentiles(db: Database, season: int, position: str, player_stats: dict) -> StatPercentiles:
    """Calculate percentile rankings for each stat within position for that season."""

    def get_percentile(stat_col: str, player_value: float) -> int:
        """Get percentile (0-100) for a stat value."""
        query = f"""
            SELECT
                COUNT(*) as below,
                (SELECT COUNT(*) FROM seasons s
                 JOIN players p ON s.gsis_id = p.gsis_id
                 WHERE s.season = ? AND p.position = ?) as total
            FROM seasons s
            JOIN players p ON s.gsis_id = p.gsis_id
            WHERE s.season = ? AND p.position = ? AND s.{stat_col} < ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(query, [season, position, season, position, player_value])
            row = cursor.fetchone()
            if row and row["total"] > 0:
                return int((row["below"] / row["total"]) * 100)
        return 50

    # Calculate half PPR for percentile
    ppr = float(player_stats["fantasy_points_ppr"] or 0)
    rec = int(player_stats["receptions"] or 0)
    half_ppr = calc_half_ppr(ppr, rec)

    # Get fantasy points percentile using calculated half PPR
    fp_query = """
        SELECT
            COUNT(*) as below,
            (SELECT COUNT(*) FROM seasons s
             JOIN players p ON s.gsis_id = p.gsis_id
             WHERE s.season = ? AND p.position = ?) as total
        FROM seasons s
        JOIN players p ON s.gsis_id = p.gsis_id
        WHERE s.season = ? AND p.position = ?
          AND (s.fantasy_points_ppr - 0.5 * s.receptions) < ?
    """
    with db.get_connection() as conn:
        cursor = conn.execute(fp_query, [season, position, season, position, half_ppr])
        row = cursor.fetchone()
        fp_percentile = int((row["below"] / row["total"]) * 100) if row and row["total"] > 0 else 50

    return StatPercentiles(
        games_played=get_percentile("games_played", player_stats["games_played"] or 0),
        pass_yards=get_percentile("pass_yards", player_stats["pass_yards"] or 0),
        pass_tds=get_percentile("pass_tds", player_stats["pass_tds"] or 0),
        rush_yards=get_percentile("rush_yards", player_stats["rush_yards"] or 0),
        rush_tds=get_percentile("rush_tds", player_stats["rush_tds"] or 0),
        receptions=get_percentile("receptions", player_stats["receptions"] or 0),
        receiving_yards=get_percentile("receiving_yards", player_stats["receiving_yards"] or 0),
        receiving_tds=get_percentile("receiving_tds", player_stats["receiving_tds"] or 0),
        fantasy_points=fp_percentile,
    )


def get_player_extra_info(db: Database, gsis_id: str) -> dict:
    """Get position, first_season, and draft info for a player."""
    query = """
        SELECT
            p.position,
            p.first_season,
            d.draft_year,
            d.round as draft_round,
            d.pick as draft_pick
        FROM players p
        LEFT JOIN draft d ON p.gsis_id = d.gsis_id
        WHERE p.gsis_id = ?
    """
    with db.get_connection() as conn:
        cursor = conn.execute(query, [gsis_id])
        row = cursor.fetchone()

    if row:
        return dict(row)
    return {}


@router.post("/find", response_model=SimilarityResponse)
def find_similar_players(
    request: SimilarityRequest,
    model: PlayerSimilarityModel = Depends(get_similarity_model),
    db: Database = Depends(get_db)
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

    # Determine which season numbers were compared
    start_season, end_season = result.comparison_range
    if start_season is None:
        start_season = 1
    if end_season is None:
        end_season = 20  # reasonable max
    season_numbers = list(range(start_season, end_season + 1))

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

    # Get aggregated stats for target player
    target_stats = get_aggregated_stats(db, target.gsis_id, season_numbers, request.mode)

    # Get season-by-season stats for target player
    target_seasons = get_player_seasons(db, target.gsis_id, season_numbers, request.mode)

    # Convert the similar players DataFrame to our schema with stats
    similar_players = []
    for _, row in result.similar_players.iterrows():
        player_gsis_id = row["gsis_id"]

        # Get extra info (position, draft info)
        extra_info = get_player_extra_info(db, player_gsis_id)

        # Get aggregated stats for this similar player
        player_stats = get_aggregated_stats(db, player_gsis_id, season_numbers, request.mode)

        similar_players.append(
            SimilarPlayer(
                gsis_id=player_gsis_id,
                name=row["name"],
                position=extra_info.get("position", ""),
                first_season=extra_info.get("first_season", 0),
                draft_year=int(extra_info["draft_year"]) if extra_info.get("draft_year") else None,
                draft_round=int(extra_info["draft_round"]) if extra_info.get("draft_round") else None,
                draft_pick=int(extra_info["draft_pick"]) if extra_info.get("draft_pick") else None,
                similarity_score=round(float(row["similarity_score"]), 4),
                euclidean_score=round(float(row["euclidean_score"]), 4) if "euclidean_score" in row and row["euclidean_score"] is not None else None,
                fantasy_score=round(float(row["fantasy_score"]), 4) if "fantasy_score" in row and row["fantasy_score"] is not None else None,
                draft_score=round(float(row["draft_score"]), 4) if "draft_score" in row and row["draft_score"] is not None else None,
                stats=player_stats
            )
        )

    return SimilarityResponse(
        target_player=target_player,
        target_stats=target_stats,
        target_seasons=target_seasons,
        similar_players=similar_players,
        comparison_mode=result.comparison_mode,
        comparison_range=result.comparison_range
    )
