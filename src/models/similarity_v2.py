"""
Player similarity analysis using the new database layer.

Supports both age-based and season-number-based comparisons.
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import Database, get_database

logger = logging.getLogger(__name__)


# Stats used for similarity calculations (core stats available 1999+)
STAT_COLUMNS = [
    'pass_yards', 'pass_tds', 'interceptions',
    'rush_yards', 'rush_tds',
    'receptions', 'receiving_yards', 'receiving_tds',
    'targets', 'fantasy_points_ppr'
]

# Position-specific stat weights
POSITION_WEIGHTS = {
    'QB': {
        'pass_yards': 1.0, 'pass_tds': 1.0, 'interceptions': 0.5,
        'rush_yards': 0.3, 'rush_tds': 0.3,
        'receptions': 0.0, 'receiving_yards': 0.0, 'receiving_tds': 0.0,
        'targets': 0.0, 'fantasy_points_ppr': 0.5
    },
    'RB': {
        'pass_yards': 0.0, 'pass_tds': 0.0, 'interceptions': 0.0,
        'rush_yards': 1.0, 'rush_tds': 1.0,
        'receptions': 0.7, 'receiving_yards': 0.7, 'receiving_tds': 0.7,
        'targets': 0.5, 'fantasy_points_ppr': 0.5
    },
    'WR': {
        'pass_yards': 0.0, 'pass_tds': 0.0, 'interceptions': 0.0,
        'rush_yards': 0.2, 'rush_tds': 0.2,
        'receptions': 1.0, 'receiving_yards': 1.0, 'receiving_tds': 1.0,
        'targets': 0.8, 'fantasy_points_ppr': 0.5
    },
    'TE': {
        'pass_yards': 0.0, 'pass_tds': 0.0, 'interceptions': 0.0,
        'rush_yards': 0.1, 'rush_tds': 0.1,
        'receptions': 1.0, 'receiving_yards': 1.0, 'receiving_tds': 1.0,
        'targets': 0.8, 'fantasy_points_ppr': 0.5
    }
}


@dataclass
class PlayerInfo:
    """Basic player information."""
    gsis_id: str
    name: str
    position: str
    first_season: int
    last_season: int
    seasons_played: int
    headshot_url: Optional[str] = None
    draft_year: Optional[int] = None
    draft_round: Optional[int] = None
    draft_pick: Optional[int] = None
    draft_position_pick: Optional[int] = None


@dataclass
class SimilarityResult:
    """Result of a similarity search."""
    target_player: PlayerInfo
    similar_players: pd.DataFrame  # Columns: gsis_id, name, similarity_score, + breakdown
    comparison_mode: str  # 'age' or 'season_number'
    comparison_range: tuple  # (min, max) of age or season_number compared


class PlayerSimilarityModel:
    """
    Calculates player similarity using multiple metrics.

    Supports two comparison modes:
    - 'age': Compare players at the same ages (original behavior)
    - 'season_number': Compare players through their first N seasons
    """

    def __init__(self, db: Optional[Database] = None):
        """
        Initialize the similarity model.

        Args:
            db: Database instance. Uses default if not provided.
        """
        self.db = db or get_database()
        self._stats_cache: Optional[pd.DataFrame] = None
        self._players_cache: Optional[pd.DataFrame] = None

    def _load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load season and player data from database."""
        if self._stats_cache is not None and self._players_cache is not None:
            return self._stats_cache, self._players_cache

        with self.db.get_connection() as conn:
            # Load seasons with player info, calculating age from birth_date
            self._stats_cache = pd.read_sql("""
                SELECT
                    s.gsis_id, s.season, s.season_number,
                    CASE
                        WHEN p.birth_date IS NOT NULL
                        THEN s.season - CAST(SUBSTR(p.birth_date, 1, 4) AS INTEGER)
                        ELSE NULL
                    END as age,
                    s.team,
                    s.games_played, s.pass_yards, s.pass_tds, s.interceptions,
                    s.rush_yards, s.rush_tds, s.receptions, s.receiving_yards,
                    s.receiving_tds, s.targets, s.fantasy_points_ppr,
                    s.passing_epa, s.rushing_epa, s.receiving_epa,
                    s.target_share, s.air_yards_share,
                    p.name, p.position
                FROM seasons s
                JOIN players p ON s.gsis_id = p.gsis_id
            """, conn)

            # Load players with draft info and headshot
            self._players_cache = pd.read_sql("""
                SELECT
                    p.gsis_id, p.name, p.position, p.first_season, p.last_season,
                    p.headshot_url,
                    d.draft_year, d.round as draft_round, d.pick as draft_pick,
                    d.position_pick as draft_position_pick
                FROM players p
                LEFT JOIN draft d ON p.gsis_id = d.gsis_id
            """, conn)

        return self._stats_cache, self._players_cache

    def get_player_info(self, gsis_id: str) -> Optional[PlayerInfo]:
        """Get information about a specific player."""
        _, players_df = self._load_data()

        player = players_df[players_df['gsis_id'] == gsis_id]
        if player.empty:
            return None

        row = player.iloc[0]
        return PlayerInfo(
            gsis_id=row['gsis_id'],
            name=row['name'],
            position=row['position'],
            first_season=row['first_season'],
            last_season=row['last_season'],
            seasons_played=row['last_season'] - row['first_season'] + 1,
            headshot_url=row.get('headshot_url'),
            draft_year=row.get('draft_year'),
            draft_round=row.get('draft_round'),
            draft_pick=row.get('draft_pick'),
            draft_position_pick=row.get('draft_position_pick')
        )

    def search_players(self, query: str, position: Optional[str] = None) -> pd.DataFrame:
        """
        Search for players by name.

        Args:
            query: Search string (partial match on name)
            position: Optional position filter (QB, RB, WR, TE)

        Returns:
            DataFrame with matching players
        """
        _, players_df = self._load_data()

        mask = players_df['name'].str.contains(query, case=False, na=False)
        if position:
            mask &= players_df['position'] == position

        results = players_df[mask].copy()
        results['seasons_played'] = results['last_season'] - results['first_season'] + 1

        return results[['gsis_id', 'name', 'position', 'first_season', 'last_season', 'seasons_played', 'headshot_url']].sort_values('name')

    def _normalize_stats(self, df: pd.DataFrame, position: str) -> pd.DataFrame:
        """
        Normalize stats for comparison using z-scores within the dataset.

        Args:
            df: DataFrame with raw stats
            position: Player position for weighting

        Returns:
            DataFrame with normalized (scaled) stats
        """
        result = df.copy()
        weights = POSITION_WEIGHTS.get(position, POSITION_WEIGHTS['WR'])

        for col in STAT_COLUMNS:
            if col in df.columns:
                # Z-score normalization
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    result[f'{col}_scaled'] = ((df[col] - mean) / std) * weights.get(col, 1.0)
                else:
                    result[f'{col}_scaled'] = 0.0

        return result

    def _calculate_euclidean_similarity(
        self,
        target_stats: pd.DataFrame,
        peer_stats: pd.DataFrame,
        comparison_col: str
    ) -> pd.DataFrame:
        """
        Calculate Euclidean distance similarity between target and peers.

        Args:
            target_stats: Target player's stats (one row per comparison unit)
            peer_stats: Peer players' stats
            comparison_col: Column to group by ('age' or 'season_number')

        Returns:
            DataFrame with similarity scores per player
        """
        scaled_cols = [c for c in target_stats.columns if c.endswith('_scaled')]

        if not scaled_cols:
            return pd.DataFrame()

        comparison_values = sorted(target_stats[comparison_col].unique())
        all_distances = {}

        for val in comparison_values:
            target_row = target_stats[target_stats[comparison_col] == val]
            peer_rows = peer_stats[peer_stats[comparison_col] == val]

            if target_row.empty or peer_rows.empty:
                continue

            target_features = target_row[scaled_cols].fillna(0).values
            peer_features = peer_rows[scaled_cols].fillna(0).values

            # Calculate Euclidean distance
            distances = cdist(peer_features, target_features, 'euclidean').flatten()

            for gsis_id, dist in zip(peer_rows['gsis_id'], distances):
                if gsis_id not in all_distances:
                    all_distances[gsis_id] = []
                all_distances[gsis_id].append(dist)

        # Average across all comparison units
        results = []
        for gsis_id, dists in all_distances.items():
            results.append({
                'gsis_id': gsis_id,
                'euclidean_score': np.mean(dists)
            })

        return pd.DataFrame(results)

    def _calculate_fantasy_similarity(
        self,
        target_stats: pd.DataFrame,
        peer_stats: pd.DataFrame,
        comparison_col: str
    ) -> pd.DataFrame:
        """
        Calculate fantasy point similarity (relative difference).

        Args:
            target_stats: Target player's stats
            peer_stats: Peer players' stats
            comparison_col: Column to group by ('age' or 'season_number')

        Returns:
            DataFrame with fantasy similarity scores per player
        """
        comparison_values = sorted(target_stats[comparison_col].unique())
        all_diffs = {}

        for val in comparison_values:
            target_row = target_stats[target_stats[comparison_col] == val]
            peer_rows = peer_stats[peer_stats[comparison_col] == val]

            if target_row.empty or peer_rows.empty:
                continue

            target_fp = target_row['fantasy_points_ppr'].iloc[0]
            if pd.isna(target_fp) or target_fp == 0:
                continue

            for _, peer_row in peer_rows.iterrows():
                gsis_id = peer_row['gsis_id']
                peer_fp = peer_row['fantasy_points_ppr']

                if pd.isna(peer_fp):
                    continue

                # Relative difference (lower is more similar)
                diff = abs(peer_fp - target_fp) / max(target_fp, 1)

                if gsis_id not in all_diffs:
                    all_diffs[gsis_id] = []
                all_diffs[gsis_id].append(diff)

        # Average across all comparison units
        results = []
        for gsis_id, diffs in all_diffs.items():
            results.append({
                'gsis_id': gsis_id,
                'fantasy_score': np.mean(diffs)
            })

        return pd.DataFrame(results)

    def _calculate_draft_similarity(
        self,
        target_info: PlayerInfo,
        peer_ids: List[str]
    ) -> pd.DataFrame:
        """
        Calculate draft position similarity.

        Args:
            target_info: Target player info with draft data
            peer_ids: List of peer player GSIS IDs

        Returns:
            DataFrame with draft similarity scores
        """
        _, players_df = self._load_data()

        # Get peer draft info
        peers = players_df[players_df['gsis_id'].isin(peer_ids)].copy()

        if target_info.draft_pick is None:
            # Target wasn't drafted or no draft data - return neutral scores
            return pd.DataFrame({
                'gsis_id': peer_ids,
                'draft_score': [0.5] * len(peer_ids)  # Neutral score
            })

        results = []
        for _, peer in peers.iterrows():
            if pd.isna(peer.get('draft_pick')):
                # Peer wasn't drafted - moderate penalty
                draft_score = 0.3
            else:
                # Calculate overall pick similarity (normalized to 7 rounds * 32 picks)
                pick_diff = abs(peer['draft_pick'] - target_info.draft_pick)
                pick_score = max(0, 1 - pick_diff / (32 * 7))

                # Calculate position pick similarity
                if target_info.draft_position_pick and peer.get('draft_position_pick'):
                    pos_diff = abs(peer['draft_position_pick'] - target_info.draft_position_pick)
                    # Assume ~15 players per position drafted on average
                    pos_score = max(0, 1 - pos_diff / 15)
                else:
                    pos_score = pick_score  # Fall back to overall pick

                # Combine (equal weight)
                draft_score = (pick_score + pos_score) / 2

            results.append({
                'gsis_id': peer['gsis_id'],
                'draft_score': draft_score
            })

        return pd.DataFrame(results)

    def find_similar_players(
        self,
        gsis_id: str,
        mode: Literal['age', 'season_number'] = 'season_number',
        max_results: int = 20,
        through_season: Optional[int] = None
    ) -> SimilarityResult:
        """
        Find players most similar to the target player.

        For season_number mode:
        - Compares the target player's first N seasons against other players' first N seasons
        - N is determined by how many seasons the target has played (or through_season if specified)
        - Only includes players who have played at least N seasons

        For age mode:
        - Compares players at the same ages

        Args:
            gsis_id: GSIS ID of the target player
            mode: Comparison mode - 'age' or 'season_number'
            max_results: Maximum number of similar players to return
            through_season: For season_number mode, compare through this season number
                           (e.g., 3 means compare first 3 seasons). If None, uses all
                           of target player's seasons.

        Returns:
            SimilarityResult with similar players and scores
        """
        stats_df, players_df = self._load_data()

        # Get target player info
        target_info = self.get_player_info(gsis_id)
        if target_info is None:
            raise ValueError(f"Player not found: {gsis_id}")

        # Get target player's stats
        target_stats = stats_df[stats_df['gsis_id'] == gsis_id].copy()
        if target_stats.empty:
            raise ValueError(f"No stats found for player: {gsis_id}")

        position = target_info.position
        comparison_col = mode  # 'age' or 'season_number'

        # Determine comparison range
        if mode == 'season_number':
            comparison_min = 1  # Always start from season 1
            if through_season is not None:
                comparison_max = min(through_season, target_stats[comparison_col].max())
            else:
                comparison_max = target_stats[comparison_col].max()

            # Filter target stats to the comparison range
            target_stats = target_stats[
                (target_stats[comparison_col] >= comparison_min) &
                (target_stats[comparison_col] <= comparison_max)
            ]
        else:
            # Age mode - use the target's actual age range
            comparison_min = target_stats[comparison_col].min()
            comparison_max = target_stats[comparison_col].max()

        # Handle NaN comparison values (e.g., age is null)
        if pd.isna(comparison_min) or pd.isna(comparison_max):
            logger.warning(f"Cannot compare by {mode} - values are null")
            return SimilarityResult(
                target_player=target_info,
                similar_players=pd.DataFrame(),
                comparison_mode=mode,
                comparison_range=(None, None)
            )

        comparison_min = int(comparison_min)
        comparison_max = int(comparison_max)
        num_comparison_units = comparison_max - comparison_min + 1

        logger.info(
            f"Finding similar players for {target_info.name} ({position}) "
            f"using {mode} range {comparison_min}-{comparison_max}"
        )

        # Get players who started their career before the target player
        # This ensures we only compare against "established" players, not contemporaries
        target_first_season = target_info.first_season
        earlier_career_players = players_df[
            players_df['first_season'] < target_first_season
        ]['gsis_id'].tolist()

        logger.info(
            f"Filtering to players who started before {target_first_season} "
            f"({len(earlier_career_players)} players)"
        )

        # Get peer players
        if mode == 'season_number':
            # For season_number mode: get peers who have data for ALL comparison seasons
            # First, find players with data for each season number in range
            peer_stats = stats_df[
                (stats_df['gsis_id'] != gsis_id) &
                (stats_df['gsis_id'].isin(earlier_career_players)) &  # Only earlier players
                (stats_df['position'] == position) &
                (stats_df[comparison_col] >= comparison_min) &
                (stats_df[comparison_col] <= comparison_max)
            ].copy()

            # Filter to peers who have data for ALL required season numbers
            peer_season_counts = peer_stats.groupby('gsis_id')[comparison_col].nunique()
            valid_peers = peer_season_counts[peer_season_counts >= num_comparison_units].index
            peer_stats = peer_stats[peer_stats['gsis_id'].isin(valid_peers)]
        else:
            # Age mode - just need overlapping ages
            peer_stats = stats_df[
                (stats_df['gsis_id'] != gsis_id) &
                (stats_df['gsis_id'].isin(earlier_career_players)) &  # Only earlier players
                (stats_df['position'] == position) &
                (stats_df[comparison_col] >= comparison_min) &
                (stats_df[comparison_col] <= comparison_max)
            ].copy()

            # Require at least 50% overlap for age mode
            min_overlap = max(1, num_comparison_units // 2)
            peer_overlap = peer_stats.groupby('gsis_id')[comparison_col].nunique()
            valid_peers = peer_overlap[peer_overlap >= min_overlap].index
            peer_stats = peer_stats[peer_stats['gsis_id'].isin(valid_peers)]

        if peer_stats.empty:
            logger.warning("No peer players found with sufficient overlap")
            return SimilarityResult(
                target_player=target_info,
                similar_players=pd.DataFrame(),
                comparison_mode=mode,
                comparison_range=(comparison_min, comparison_max)
            )

        # Normalize stats
        all_stats = pd.concat([target_stats, peer_stats])
        all_stats_normalized = self._normalize_stats(all_stats, position)

        target_normalized = all_stats_normalized[all_stats_normalized['gsis_id'] == gsis_id]
        peer_normalized = all_stats_normalized[all_stats_normalized['gsis_id'] != gsis_id]

        # Calculate similarity components
        euclidean_scores = self._calculate_euclidean_similarity(
            target_normalized, peer_normalized, comparison_col
        )
        fantasy_scores = self._calculate_fantasy_similarity(
            target_normalized, peer_normalized, comparison_col
        )

        # Merge scores
        if euclidean_scores.empty and fantasy_scores.empty:
            return SimilarityResult(
                target_player=target_info,
                similar_players=pd.DataFrame(),
                comparison_mode=mode,
                comparison_range=(comparison_min, comparison_max)
            )

        # Start with euclidean scores
        scores = euclidean_scores.copy() if not euclidean_scores.empty else pd.DataFrame({'gsis_id': []})

        if not fantasy_scores.empty:
            scores = scores.merge(fantasy_scores, on='gsis_id', how='outer')

        # Add draft similarity
        draft_scores = self._calculate_draft_similarity(target_info, scores['gsis_id'].tolist())
        scores = scores.merge(draft_scores, on='gsis_id', how='left')

        # Fill missing scores (only numeric columns)
        numeric_cols = scores.select_dtypes(include=[np.number]).columns
        scores[numeric_cols] = scores[numeric_cols].fillna(scores[numeric_cols].mean())

        # Calculate combined score
        # Normalize each component to 0-1 range first
        for col in ['euclidean_score', 'fantasy_score']:
            if col in scores.columns:
                min_val = scores[col].min()
                max_val = scores[col].max()
                if max_val > min_val:
                    scores[f'{col}_norm'] = (scores[col] - min_val) / (max_val - min_val)
                else:
                    scores[f'{col}_norm'] = 0.5

        # Combined score (lower is more similar)
        # Weight: 40% euclidean, 40% fantasy, 20% draft (inverted since higher draft = more similar)
        stat_score = 0
        if 'euclidean_score_norm' in scores.columns:
            stat_score += 0.4 * scores['euclidean_score_norm']
        if 'fantasy_score_norm' in scores.columns:
            stat_score += 0.4 * scores['fantasy_score_norm']

        draft_component = 0.2 * (1 - scores['draft_score'].fillna(0.5))
        scores['similarity_score'] = stat_score + draft_component

        # Add player names
        scores = scores.merge(
            players_df[['gsis_id', 'name', 'first_season', 'last_season']],
            on='gsis_id',
            how='left'
        )

        # Sort by similarity (lower is more similar)
        scores = scores.sort_values('similarity_score').head(max_results)

        # Select final columns
        result_cols = ['gsis_id', 'name', 'similarity_score', 'euclidean_score', 'fantasy_score', 'draft_score']
        result_cols = [c for c in result_cols if c in scores.columns]

        return SimilarityResult(
            target_player=target_info,
            similar_players=scores[result_cols].reset_index(drop=True),
            comparison_mode=mode,
            comparison_range=(comparison_min, comparison_max)
        )

    def get_comparison_data(
        self,
        target_gsis_id: str,
        compare_gsis_ids: List[str],
        mode: Literal['age', 'season_number'] = 'season_number'
    ) -> pd.DataFrame:
        """
        Get detailed comparison data between target and selected players.

        Useful for visualization.

        Args:
            target_gsis_id: Target player GSIS ID
            compare_gsis_ids: List of player GSIS IDs to compare
            mode: Comparison mode

        Returns:
            DataFrame with stats for all players by comparison unit
        """
        stats_df, players_df = self._load_data()

        all_ids = [target_gsis_id] + compare_gsis_ids

        comparison_data = stats_df[stats_df['gsis_id'].isin(all_ids)].copy()
        comparison_data = comparison_data.merge(
            players_df[['gsis_id', 'name']],
            on='gsis_id',
            how='left'
        )

        # Mark the target player
        comparison_data['is_target'] = comparison_data['gsis_id'] == target_gsis_id

        return comparison_data.sort_values([mode, 'is_target'], ascending=[True, False])
