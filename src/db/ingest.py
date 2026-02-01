"""
Data ingestion pipeline for NFL Player Similarity.

Fetches data from nflreadpy (nflverse) and loads it into the SQLite database.
"""

import logging
from typing import Optional
from pathlib import Path

import pandas as pd

from .database import Database, get_database

logger = logging.getLogger(__name__)

# Positions we care about
SKILL_POSITIONS = {"QB", "RB", "WR", "TE"}

# Season range
MIN_SEASON = 1999
MAX_SEASON = 2024  # Update when new season data becomes available (2025 not yet in nflverse)


class DataIngester:
    """Handles data ingestion from nflreadpy to SQLite."""

    def __init__(self, db: Optional[Database] = None):
        """
        Initialize the data ingester.

        Args:
            db: Database instance. Uses default if not provided.
        """
        self.db = db or get_database()
        self._player_ids_df: Optional[pd.DataFrame] = None
        self._rosters_df: Optional[pd.DataFrame] = None

    def _import_nflreadpy(self):
        """Import nflreadpy with fallback to nfl_data_py."""
        try:
            import nflreadpy as nfl
            self._use_polars = True
            return nfl
        except ImportError:
            try:
                import nfl_data_py as nfl
                self._use_polars = False
                logger.info("Using nfl_data_py (nflreadpy not available)")
                return nfl
            except ImportError:
                raise ImportError(
                    "Neither nflreadpy nor nfl_data_py is installed. "
                    "Please install with: pip install nflreadpy"
                )

    def _to_pandas(self, df) -> pd.DataFrame:
        """Convert to pandas DataFrame if needed."""
        if self._use_polars and hasattr(df, 'to_pandas'):
            return df.to_pandas()
        return df

    def fetch_player_ids(self) -> pd.DataFrame:
        """
        Fetch player ID mappings from nflverse.

        Returns:
            DataFrame with player ID mappings (gsis_id, pfr_id, espn_id, etc.)
        """
        if self._player_ids_df is not None:
            return self._player_ids_df

        nfl = self._import_nflreadpy()

        logger.info("Fetching player ID mappings...")
        if self._use_polars:
            df = nfl.load_ff_playerids()
        else:
            df = nfl.import_ids()

        self._player_ids_df = self._to_pandas(df)
        logger.info(f"Fetched {len(self._player_ids_df)} player ID mappings")
        return self._player_ids_df

    def fetch_rosters(self, seasons: Optional[list] = None) -> pd.DataFrame:
        """
        Fetch roster data for player biographical info and position.

        Args:
            seasons: List of seasons to fetch. Defaults to all.

        Returns:
            DataFrame with roster/biographical data including position
        """
        if self._rosters_df is not None:
            return self._rosters_df

        nfl = self._import_nflreadpy()
        seasons = seasons or list(range(MIN_SEASON, MAX_SEASON + 1))

        logger.info(f"Fetching roster data for {len(seasons)} seasons...")
        if self._use_polars:
            df = nfl.load_rosters(seasons)
        else:
            # nfl_data_py uses import_seasonal_rosters
            df = nfl.import_seasonal_rosters(seasons)

        self._rosters_df = self._to_pandas(df)
        logger.info(f"Fetched {len(self._rosters_df)} roster records")
        return self._rosters_df

    def fetch_seasonal_stats(self, seasons: Optional[list] = None) -> pd.DataFrame:
        """
        Fetch seasonal player statistics.

        Args:
            seasons: List of seasons to fetch. Defaults to 1999-2025.

        Returns:
            DataFrame with seasonal statistics
        """
        nfl = self._import_nflreadpy()
        seasons = seasons or list(range(MIN_SEASON, MAX_SEASON + 1))

        logger.info(f"Fetching seasonal stats for {len(seasons)} seasons...")
        if self._use_polars:
            df = nfl.load_player_stats(seasons, stat_type="season")
        else:
            df = nfl.import_seasonal_data(seasons)

        df = self._to_pandas(df)
        logger.info(f"Fetched {len(df)} seasonal stat records")
        return df

    def fetch_draft_data(self, seasons: Optional[list] = None) -> pd.DataFrame:
        """
        Fetch draft data.

        Args:
            seasons: List of draft years to fetch. Defaults to 2000-2025.

        Returns:
            DataFrame with draft picks
        """
        nfl = self._import_nflreadpy()
        # Draft data starts from 2000 in nflverse
        seasons = seasons or list(range(2000, MAX_SEASON + 1))

        logger.info(f"Fetching draft data for {len(seasons)} years...")
        if self._use_polars:
            df = nfl.load_draft_picks(seasons)
        else:
            df = nfl.import_draft_picks(seasons)

        df = self._to_pandas(df)
        logger.info(f"Fetched {len(df)} draft records")
        return df

    def _add_position_and_name_to_stats(
        self,
        stats_df: pd.DataFrame,
        ids_df: pd.DataFrame,
        rosters_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Add position and player_name to stats DataFrame by joining from IDs or rosters.

        Args:
            stats_df: Seasonal stats DataFrame (no position/name columns)
            ids_df: Player ID mappings DataFrame
            rosters_df: Roster data DataFrame

        Returns:
            Stats DataFrame with position and player_name columns added
        """
        df = stats_df.copy()

        # Get position and name from ID mappings
        if 'gsis_id' in ids_df.columns:
            id_cols_to_get = ['gsis_id']
            if 'position' in ids_df.columns:
                id_cols_to_get.append('position')
            if 'name' in ids_df.columns:
                id_cols_to_get.append('name')

            if len(id_cols_to_get) > 1:
                id_info = ids_df[id_cols_to_get].drop_duplicates(subset=['gsis_id'])
                df = df.merge(id_info, left_on='player_id', right_on='gsis_id', how='left')
                df = df.drop(columns=['gsis_id'], errors='ignore')

                # Rename 'name' to 'player_name' if it exists
                if 'name' in df.columns:
                    df = df.rename(columns={'name': 'player_name'})

                logger.info(f"Joined from IDs: {df['position'].notna().sum()}/{len(df)} have position")

        # Fill remaining from rosters
        if 'position' not in df.columns or df['position'].isna().any():
            if 'player_id' in rosters_df.columns and 'position' in rosters_df.columns:
                # Get most common position and name per player from rosters
                roster_info = rosters_df.groupby('player_id').agg({
                    'position': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0],
                    'player_name': 'first'
                }).reset_index()
                roster_info.columns = ['player_id', 'roster_position', 'roster_name']

                df = df.merge(roster_info, on='player_id', how='left')

                # Fill in missing values
                if 'position' in df.columns:
                    df['position'] = df['position'].fillna(df['roster_position'])
                else:
                    df['position'] = df['roster_position']

                if 'player_name' not in df.columns:
                    df['player_name'] = df['roster_name']
                else:
                    df['player_name'] = df['player_name'].fillna(df['roster_name'])

                df = df.drop(columns=['roster_position', 'roster_name'], errors='ignore')
                logger.info(f"After roster join: {df['position'].notna().sum()}/{len(df)} have position")

        # Ensure player_name exists
        if 'player_name' not in df.columns:
            df['player_name'] = None

        return df

    def _build_players_table(
        self,
        stats_df: pd.DataFrame,
        ids_df: pd.DataFrame,
        rosters_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Build the players table from multiple data sources.

        Args:
            stats_df: Seasonal stats DataFrame (with position column added)
            ids_df: Player ID mappings DataFrame
            rosters_df: Roster/bio data DataFrame

        Returns:
            DataFrame ready for players table insertion
        """
        # Filter to skill positions only
        stats_filtered = stats_df[stats_df['position'].isin(SKILL_POSITIONS)].copy()

        # Group by player to get their most common position and career span
        player_stats = stats_filtered.groupby('player_id').agg({
            'player_name': 'first',
            'position': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0],
            'season': ['min', 'max']
        }).reset_index()

        player_stats.columns = ['gsis_id', 'name', 'position', 'first_season', 'last_season']

        # Merge with ID mappings to get PFR ID, ESPN ID, etc.
        id_cols = ['gsis_id']
        for col in ['pfr_id', 'espn_id', 'sleeper_id']:
            if col in ids_df.columns:
                id_cols.append(col)

        if 'gsis_id' in ids_df.columns and len(id_cols) > 1:
            ids_subset = ids_df[id_cols].drop_duplicates(subset=['gsis_id'])
            player_stats = player_stats.merge(ids_subset, on='gsis_id', how='left')

        # Merge with rosters to get biographical info
        # Get most recent roster entry per player for bio data
        if 'player_id' in rosters_df.columns:
            roster_bio = rosters_df.sort_values('season', ascending=False).drop_duplicates(
                subset=['player_id'], keep='first'
            )

            bio_cols = ['player_id']
            col_mapping = {
                'height': 'height_inches',
                'weight': 'weight',
                'birth_date': 'birth_date',
            }
            for src, dst in col_mapping.items():
                if src in roster_bio.columns:
                    bio_cols.append(src)

            if len(bio_cols) > 1:
                roster_subset = roster_bio[bio_cols].copy()
                roster_subset.columns = ['gsis_id'] + [col_mapping[c] for c in bio_cols[1:]]
                player_stats = player_stats.merge(roster_subset, on='gsis_id', how='left')

        # Ensure all expected columns exist
        for col in ['pfr_id', 'espn_id', 'sleeper_id', 'height_inches', 'weight', 'birth_date']:
            if col not in player_stats.columns:
                player_stats[col] = None

        logger.info(f"Built players table with {len(player_stats)} players")
        return player_stats

    def _build_seasons_table(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """
        Build the seasons table from seasonal stats.

        Args:
            stats_df: Seasonal stats DataFrame

        Returns:
            DataFrame ready for seasons table insertion
        """
        # Filter to skill positions
        df = stats_df[stats_df['position'].isin(SKILL_POSITIONS)].copy()

        # Calculate season number for each player
        df = df.sort_values(['player_id', 'season'])
        df['season_number'] = df.groupby('player_id').cumcount() + 1

        # Map nflverse columns to our schema
        column_mapping = {
            'player_id': 'gsis_id',
            'season': 'season',
            'season_number': 'season_number',
            'age': 'age',
            'recent_team': 'team',
            'games': 'games_played',

            # Passing
            'completions': 'pass_completions',
            'attempts': 'pass_attempts',
            'passing_yards': 'pass_yards',
            'passing_tds': 'pass_tds',
            'interceptions': 'interceptions',
            'sacks': 'sacks',
            'sack_yards': 'sack_yards',

            # Rushing
            'carries': 'rush_attempts',
            'rushing_yards': 'rush_yards',
            'rushing_tds': 'rush_tds',

            # Receiving
            'targets': 'targets',
            'receptions': 'receptions',
            'receiving_yards': 'receiving_yards',
            'receiving_tds': 'receiving_tds',

            # Fumbles
            'sack_fumbles': 'fumbles',  # Note: may need to combine multiple fumble columns

            # EPA
            'passing_epa': 'passing_epa',
            'rushing_epa': 'rushing_epa',
            'receiving_epa': 'receiving_epa',

            # Air yards / YAC
            'passing_air_yards': 'passing_air_yards',
            'passing_yards_after_catch': 'passing_yac',
            'receiving_air_yards': 'receiving_air_yards',
            'receiving_yards_after_catch': 'receiving_yac',

            # First downs
            'passing_first_downs': 'passing_first_downs',
            'rushing_first_downs': 'rushing_first_downs',
            'receiving_first_downs': 'receiving_first_downs',

            # Share stats
            'target_share': 'target_share',
            'air_yards_share': 'air_yards_share',

            # Fantasy points
            'fantasy_points_ppr': 'fantasy_points_ppr',
        }

        # Select and rename columns that exist
        available_cols = [c for c in column_mapping.keys() if c in df.columns]
        result = df[available_cols].rename(
            columns={k: v for k, v in column_mapping.items() if k in available_cols}
        )

        # Calculate position rank within each season
        # Using fantasy points PPR as the ranking metric
        if 'fantasy_points_ppr' in result.columns:
            # Need to join back with position
            result = result.merge(
                df[['player_id', 'season', 'position']].rename(columns={'player_id': 'gsis_id'}),
                on=['gsis_id', 'season'],
                how='left'
            )
            result['position_rank'] = result.groupby(['season', 'position'])['fantasy_points_ppr'].rank(
                ascending=False, method='min'
            )
            result = result.drop(columns=['position'])

        # Ensure all expected columns exist with defaults
        expected_cols = [
            'gsis_id', 'season', 'season_number', 'age', 'team', 'games_played',
            'games_started', 'pass_completions', 'pass_attempts', 'pass_yards',
            'pass_tds', 'interceptions', 'sacks', 'sack_yards', 'rush_attempts',
            'rush_yards', 'rush_tds', 'targets', 'receptions', 'receiving_yards',
            'receiving_tds', 'fumbles', 'fumbles_lost', 'passing_epa', 'rushing_epa',
            'receiving_epa', 'passing_air_yards', 'passing_yac', 'receiving_air_yards',
            'receiving_yac', 'passing_first_downs', 'rushing_first_downs',
            'receiving_first_downs', 'target_share', 'air_yards_share', 'rush_share',
            'fantasy_points_ppr', 'fantasy_points_half_ppr', 'fantasy_points_standard',
            'position_rank'
        ]

        for col in expected_cols:
            if col not in result.columns:
                result[col] = None

        logger.info(f"Built seasons table with {len(result)} records")
        return result[expected_cols]

    def _build_draft_table(self, draft_df: pd.DataFrame, ids_df: pd.DataFrame) -> pd.DataFrame:
        """
        Build the draft table.

        Args:
            draft_df: Draft data DataFrame
            ids_df: Player ID mappings for GSIS ID lookup

        Returns:
            DataFrame ready for draft table insertion
        """
        # Filter to skill positions
        df = draft_df[draft_df['position'].isin(SKILL_POSITIONS)].copy()

        # The draft data may have different ID columns
        # Try to get gsis_id from the ID mappings
        if 'gsis_id' not in df.columns and 'pfr_id' in df.columns and 'pfr_id' in ids_df.columns:
            id_mapping = ids_df[['gsis_id', 'pfr_id']].drop_duplicates()
            df = df.merge(id_mapping, on='pfr_id', how='left')
        elif 'gsis_id' not in df.columns and 'pfr_player_id' in df.columns:
            # nfl_data_py uses pfr_player_id
            if 'pfr_id' in ids_df.columns:
                id_mapping = ids_df[['gsis_id', 'pfr_id']].drop_duplicates()
                df = df.merge(
                    id_mapping,
                    left_on='pfr_player_id',
                    right_on='pfr_id',
                    how='left'
                )

        # Calculate position pick (nth player at position in that draft)
        df = df.sort_values(['season', 'pick'])
        df['position_pick'] = df.groupby(['season', 'position']).cumcount() + 1

        # Map columns
        column_mapping = {
            'gsis_id': 'gsis_id',
            'season': 'draft_year',
            'round': 'round',
            'pick': 'pick',
            'position_pick': 'position_pick',
            'team': 'team',
        }

        available_cols = [c for c in column_mapping.keys() if c in df.columns]
        result = df[available_cols].rename(
            columns={k: v for k, v in column_mapping.items() if k in available_cols}
        )

        # Filter out records without gsis_id (can't link to players)
        if 'gsis_id' in result.columns:
            before = len(result)
            result = result.dropna(subset=['gsis_id'])
            after = len(result)
            if before > after:
                logger.warning(f"Dropped {before - after} draft records without gsis_id")

        logger.info(f"Built draft table with {len(result)} records")
        return result

    def ingest_all(
        self,
        seasons: Optional[list] = None,
        force: bool = False
    ) -> dict:
        """
        Run the full ingestion pipeline.

        Args:
            seasons: Seasons to ingest. Defaults to 1999-2025.
            force: If True, reinitialize database before ingesting.

        Returns:
            Dictionary with ingestion statistics
        """
        seasons = seasons or list(range(MIN_SEASON, MAX_SEASON + 1))

        # Initialize database
        self.db.initialize(force=force)

        # Fetch all data
        logger.info("Starting data fetch from nflverse...")
        ids_df = self.fetch_player_ids()
        rosters_df = self.fetch_rosters(seasons)
        stats_df = self.fetch_seasonal_stats(seasons)
        draft_df = self.fetch_draft_data([s for s in seasons if s >= 2000])

        # Add position and name to stats (stats don't have these natively)
        logger.info("Adding position and name data to stats...")
        stats_with_pos = self._add_position_and_name_to_stats(stats_df, ids_df, rosters_df)

        # Build tables
        logger.info("Building database tables...")
        players_df = self._build_players_table(stats_with_pos, ids_df, rosters_df)
        seasons_df = self._build_seasons_table(stats_with_pos)
        draft_table_df = self._build_draft_table(draft_df, ids_df)

        # Insert into database
        logger.info("Inserting data into database...")
        with self.db.get_connection() as conn:
            # Insert players
            players_df.to_sql('players', conn, if_exists='append', index=False)

            # Insert seasons
            seasons_df.to_sql('seasons', conn, if_exists='append', index=False)

            # Insert draft (only for players we have)
            # Filter to players that exist in our players table
            existing_players = set(players_df['gsis_id'].dropna())
            draft_filtered = draft_table_df[
                draft_table_df['gsis_id'].isin(existing_players)
            ]
            draft_filtered.to_sql('draft', conn, if_exists='append', index=False)

        # Return stats
        stats = self.db.get_stats()
        logger.info(f"Ingestion complete: {stats}")
        return stats


def run_ingestion(
    db_path: Optional[Path] = None,
    seasons: Optional[list] = None,
    force: bool = False
) -> dict:
    """
    Convenience function to run the full ingestion pipeline.

    Args:
        db_path: Path to database file.
        seasons: Seasons to ingest.
        force: If True, reinitialize database.

    Returns:
        Dictionary with ingestion statistics
    """
    db = Database(db_path) if db_path else get_database()
    ingester = DataIngester(db)
    return ingester.ingest_all(seasons=seasons, force=force)


if __name__ == "__main__":
    # Run ingestion when executed directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stats = run_ingestion(force=True)
    print(f"\nIngestion complete!")
    print(f"  Players: {stats['total_players']}")
    print(f"  By position: {stats['players_by_position']}")
    print(f"  Season records: {stats['total_season_records']}")
    print(f"  Season range: {stats['season_range']}")
    print(f"  Draft records: {stats['draft_records']}")
