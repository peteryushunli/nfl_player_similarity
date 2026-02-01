-- NFL Player Similarity Database Schema
-- Core stats version (1999-present)
-- Enhanced stats columns can be added later (NGS 2016+, PFR Advanced 2018+)

-- Players table: Core player identity and biographical info
CREATE TABLE IF NOT EXISTS players (
    -- Primary identifier (NFL's Game Statistics & Information System ID)
    gsis_id TEXT PRIMARY KEY,

    -- Alternative IDs for cross-referencing
    pfr_id TEXT,                    -- Pro Football Reference ID
    espn_id TEXT,
    sleeper_id TEXT,

    -- Biographical info
    name TEXT NOT NULL,
    position TEXT NOT NULL,         -- QB, RB, WR, TE

    -- Physical attributes (nullable - not always available)
    height_inches INTEGER,
    weight INTEGER,
    birth_date TEXT,

    -- Career span (calculated from seasons data)
    first_season INTEGER,
    last_season INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Draft table: Draft capital information
CREATE TABLE IF NOT EXISTS draft (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gsis_id TEXT NOT NULL,

    -- Draft details
    draft_year INTEGER NOT NULL,
    round INTEGER NOT NULL,
    pick INTEGER NOT NULL,          -- Overall pick number
    position_pick INTEGER,          -- Position-specific pick (e.g., 3rd WR taken)

    -- Team that drafted them
    team TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (gsis_id) REFERENCES players(gsis_id),
    UNIQUE(gsis_id)                 -- One draft record per player
);

-- Seasons table: Per-season statistics
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gsis_id TEXT NOT NULL,
    season INTEGER NOT NULL,

    -- Season context
    season_number INTEGER,          -- 1st season, 2nd season, etc. (calculated)
    age INTEGER,
    team TEXT,
    games_played INTEGER,
    games_started INTEGER,

    -- ===================
    -- CORE STATS (1999+)
    -- ===================

    -- Passing stats
    pass_completions INTEGER DEFAULT 0,
    pass_attempts INTEGER DEFAULT 0,
    pass_yards INTEGER DEFAULT 0,
    pass_tds INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    sacks INTEGER DEFAULT 0,
    sack_yards INTEGER DEFAULT 0,

    -- Rushing stats
    rush_attempts INTEGER DEFAULT 0,
    rush_yards INTEGER DEFAULT 0,
    rush_tds INTEGER DEFAULT 0,

    -- Receiving stats
    targets INTEGER DEFAULT 0,
    receptions INTEGER DEFAULT 0,
    receiving_yards INTEGER DEFAULT 0,
    receiving_tds INTEGER DEFAULT 0,

    -- Fumbles
    fumbles INTEGER DEFAULT 0,
    fumbles_lost INTEGER DEFAULT 0,

    -- ===================
    -- EFFICIENCY STATS (1999+, from play-by-play)
    -- ===================

    -- EPA (Expected Points Added)
    passing_epa REAL,
    rushing_epa REAL,
    receiving_epa REAL,

    -- Air yards / YAC split
    passing_air_yards INTEGER,          -- QB: total air yards thrown
    passing_yac INTEGER,                -- QB: team YAC on completions
    receiving_air_yards INTEGER,        -- WR/TE/RB: air yards on targets
    receiving_yac INTEGER,              -- WR/TE/RB: yards after catch

    -- First downs
    passing_first_downs INTEGER,
    rushing_first_downs INTEGER,
    receiving_first_downs INTEGER,

    -- ===================
    -- SHARE/USAGE STATS (calculated)
    -- ===================

    target_share REAL,                  -- targets / team pass attempts
    air_yards_share REAL,               -- air yards / team air yards
    rush_share REAL,                    -- rush attempts / team rush attempts

    -- Fantasy points (for reference/projections)
    fantasy_points_ppr REAL,
    fantasy_points_half_ppr REAL,
    fantasy_points_standard REAL,

    -- Position rank (within season)
    position_rank INTEGER,

    -- ===================
    -- PLACEHOLDER FOR ENHANCED STATS (to be added later)
    -- ===================
    -- NGS stats (2016+): separation, cushion, RYOE, time_to_throw, etc.
    -- PFR Advanced (2018+): broken_tackles, yards_after_contact, adot, etc.
    -- These columns will be added in a future migration

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (gsis_id) REFERENCES players(gsis_id),
    UNIQUE(gsis_id, season)             -- One record per player per season
);

-- ===================
-- INDEXES
-- ===================

-- Player lookups
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_pfr_id ON players(pfr_id);

-- Season queries
CREATE INDEX IF NOT EXISTS idx_seasons_gsis_id ON seasons(gsis_id);
CREATE INDEX IF NOT EXISTS idx_seasons_season ON seasons(season);
CREATE INDEX IF NOT EXISTS idx_seasons_season_number ON seasons(season_number);
CREATE INDEX IF NOT EXISTS idx_seasons_position_rank ON seasons(position_rank);

-- Draft queries
CREATE INDEX IF NOT EXISTS idx_draft_year ON draft(draft_year);
CREATE INDEX IF NOT EXISTS idx_draft_pick ON draft(pick);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_seasons_player_season ON seasons(gsis_id, season);
CREATE INDEX IF NOT EXISTS idx_seasons_season_position ON seasons(season, position_rank);

-- ===================
-- VIEWS
-- ===================

-- View: Player career summary
CREATE VIEW IF NOT EXISTS player_career_summary AS
SELECT
    p.gsis_id,
    p.name,
    p.position,
    p.first_season,
    p.last_season,
    (p.last_season - p.first_season + 1) as seasons_played,
    d.draft_year,
    d.round as draft_round,
    d.pick as draft_pick,
    d.position_pick as draft_position_pick,
    SUM(s.games_played) as career_games,
    SUM(s.pass_yards) as career_pass_yards,
    SUM(s.pass_tds) as career_pass_tds,
    SUM(s.rush_yards) as career_rush_yards,
    SUM(s.rush_tds) as career_rush_tds,
    SUM(s.receiving_yards) as career_receiving_yards,
    SUM(s.receiving_tds) as career_receiving_tds,
    SUM(s.fantasy_points_ppr) as career_fantasy_points_ppr
FROM players p
LEFT JOIN draft d ON p.gsis_id = d.gsis_id
LEFT JOIN seasons s ON p.gsis_id = s.gsis_id
GROUP BY p.gsis_id;

-- View: Seasons with player info (denormalized for easy querying)
CREATE VIEW IF NOT EXISTS seasons_with_player AS
SELECT
    s.*,
    p.name,
    p.position,
    p.pfr_id,
    d.draft_year,
    d.round as draft_round,
    d.pick as draft_pick,
    d.position_pick as draft_position_pick
FROM seasons s
JOIN players p ON s.gsis_id = p.gsis_id
LEFT JOIN draft d ON s.gsis_id = d.gsis_id;
