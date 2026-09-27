"""
Checks that data/nfl_similarity.db still satisfies the fantasy hub's data contract.

fantasy_football_manager_hub/scripts/push-nfl-comps.mjs reads the columns in
CONTRACT (keep it in sync with that script's SELECTs) and refuses to push when
its sanity checks fail. These tests mirror those checks, plus a few the script
doesn't make, so a bad ingest fails here before it gets near Supabase.
"""

import sqlite3
from datetime import date

import pytest

from src.db.database import DEFAULT_DB_PATH, Database
from src.db.ingest import MAX_SEASON, MIN_SEASON, SKILL_POSITIONS, latest_completed_season

CONTRACT = {
    "players": {
        "gsis_id", "name", "position", "birth_date", "first_season", "last_season",
        "headshot_url", "espn_id", "sleeper_id",
    },
    "draft": {"gsis_id", "draft_year", "round", "pick", "position_pick", "team"},
    "seasons": {
        "gsis_id", "season", "season_number", "team", "games_played", "games_started",
        "pass_completions", "pass_attempts", "pass_yards", "pass_tds", "interceptions",
        "rush_attempts", "rush_yards", "rush_tds", "targets", "receptions",
        "receiving_yards", "receiving_tds", "fantasy_points_ppr",
    },
}


def columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def count(conn, sql):
    return conn.execute(sql).fetchone()[0]


def test_schema_defines_contract_columns(tmp_path):
    db = Database(tmp_path / "schema_only.db")
    db.initialize()
    with db.get_connection() as conn:
        for table, cols in CONTRACT.items():
            assert cols <= columns(conn, table), f"{table} is missing {cols - columns(conn, table)}"


@pytest.mark.parametrize("today, season", [
    (date(2026, 9, 27), 2025),  # 2026 season under way
    (date(2027, 1, 5), 2025),   # 2026 regular season still wrapping up
    (date(2027, 2, 1), 2026),
    (date(2027, 8, 31), 2026),
])
def test_latest_completed_season(today, season):
    assert latest_completed_season(today) == season


@pytest.fixture(scope="module")
def built_db():
    if not DEFAULT_DB_PATH.exists():
        pytest.skip(f"{DEFAULT_DB_PATH} not built yet; run python -m src.db.ingest")
    conn = sqlite3.connect(f"file:{DEFAULT_DB_PATH}?mode=ro", uri=True)
    yield conn
    conn.close()


def test_built_db_has_contract_columns(built_db):
    for table, cols in CONTRACT.items():
        assert cols <= columns(built_db, table), f"{table} is missing {cols - columns(built_db, table)}"


def test_built_db_passes_push_sanity_checks(built_db):
    # The checks push-nfl-comps.mjs refuses to push on
    positions = {row[0] for row in built_db.execute("SELECT DISTINCT position FROM players")}
    assert positions <= SKILL_POSITIONS
    assert count(built_db, "SELECT COUNT(*) FROM players WHERE first_season IS NULL OR last_season IS NULL") == 0
    assert count(built_db, "SELECT COUNT(*) FROM seasons WHERE gsis_id NOT IN (SELECT gsis_id FROM players)") == 0
    assert count(built_db, "SELECT COUNT(*) FROM seasons WHERE season_number IS NULL") == 0


def test_built_db_careers_are_consistent(built_db):
    # season_number counts each player's seasons 1, 2, 3...; the comps model aligns careers on it
    assert count(built_db, """
        SELECT COUNT(*) FROM (
            SELECT season_number, ROW_NUMBER() OVER (PARTITION BY gsis_id ORDER BY season) AS n
            FROM seasons
        ) WHERE season_number != n
    """) == 0
    # Every player has seasons, and first/last season match them
    assert count(built_db, """
        SELECT COUNT(*) FROM players p
        LEFT JOIN (SELECT gsis_id, MIN(season) AS lo, MAX(season) AS hi FROM seasons GROUP BY gsis_id) s
          USING (gsis_id)
        WHERE s.lo IS NULL OR p.first_season != s.lo OR p.last_season != s.hi
    """) == 0
    assert count(built_db, "SELECT COUNT(*) FROM draft WHERE gsis_id NOT IN (SELECT gsis_id FROM players)") == 0


def test_built_db_covers_completed_seasons(built_db):
    seasons = [row[0] for row in built_db.execute("SELECT DISTINCT season FROM seasons ORDER BY season")]
    assert seasons[0] == MIN_SEASON
    assert seasons == list(range(MIN_SEASON, seasons[-1] + 1)), "a season is missing"
    assert seasons[-1] <= MAX_SEASON, f"{seasons[-1]} isn't over yet"
    # A finished regular season has players with a full slate of games (16 through 2020, 17 since)
    assert count(built_db, f"SELECT MAX(games_played) FROM seasons WHERE season = {seasons[-1]}") >= 16


def test_built_db_ids_and_dates_are_clean(built_db):
    for col in ("espn_id", "sleeper_id"):
        assert count(built_db, f"""
            SELECT COUNT(*) FROM players
            WHERE {col} IS NOT NULL AND (typeof({col}) != 'text' OR {col} = '' OR {col} GLOB '*[^0-9]*')
        """) == 0, f"{col} should hold digit strings like '331', not '331.0'"
    assert count(built_db, """
        SELECT COUNT(*) FROM players
        WHERE birth_date IS NOT NULL AND birth_date NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    """) == 0, "birth_date should be YYYY-MM-DD"


def test_built_db_joins_filled_player_fields(built_db):
    # Floors well under the 2026 build's coverage (espn 72%, sleeper 57%, birth date 94%,
    # headshot 100%, drafted 63%), to catch a join that silently stopped matching
    floors = {"espn_id": 0.5, "sleeper_id": 0.4, "birth_date": 0.8, "headshot_url": 0.8}
    players = count(built_db, "SELECT COUNT(*) FROM players")
    for col, floor in floors.items():
        assert count(built_db, f"SELECT COUNT({col}) FROM players") >= floor * players, f"{col} coverage dropped"
    assert count(built_db, "SELECT COUNT(*) FROM draft") >= 0.4 * players, "draft coverage dropped"
