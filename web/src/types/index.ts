/**
 * TypeScript type definitions for the NFL Player Similarity app.
 *
 * These types match the API response shapes from our FastAPI backend.
 * Having types defined helps catch errors early and provides better
 * autocomplete in your editor.
 */

/**
 * Basic player information (used in search results).
 */
export interface PlayerSummary {
  gsis_id: string;
  name: string;
  position: 'QB' | 'RB' | 'WR' | 'TE';
  first_season: number;
  last_season: number;
  seasons_played: number;
}

/**
 * Detailed player information including draft data.
 */
export interface PlayerInfo extends PlayerSummary {
  draft_year: number | null;
  draft_round: number | null;
  draft_pick: number | null;
  draft_position_pick: number | null;
}

/**
 * Percentile rankings (0-100, higher = better) for heatmap coloring.
 */
export interface StatPercentiles {
  games_played: number | null;
  pass_yards: number | null;
  pass_tds: number | null;
  rush_yards: number | null;
  rush_tds: number | null;
  receptions: number | null;
  receiving_yards: number | null;
  receiving_tds: number | null;
  fantasy_points: number | null;
}

/**
 * Stats for a single season.
 */
export interface SeasonStats {
  season: number;
  season_number: number;
  age: number | null;
  games_played: number;
  games_started: number;
  // Passing
  pass_completions: number;
  pass_attempts: number;
  pass_yards: number;
  pass_tds: number;
  interceptions: number;
  // Rushing
  rush_attempts: number;
  rush_yards: number;
  rush_tds: number;
  // Receiving
  targets: number;
  receptions: number;
  receiving_yards: number;
  receiving_tds: number;
  // Fantasy (half PPR)
  fantasy_points: number;
  // Rankings (based on half PPR)
  fantasy_position_rank: number | null;
  fantasy_overall_rank: number | null;
  // Percentiles for heatmap
  percentiles: StatPercentiles | null;
}

/**
 * Aggregated stats across multiple seasons.
 */
export interface AggregatedStats {
  seasons_included: number[];
  games_played: number;
  games_started: number;
  // Passing
  pass_completions: number;
  pass_attempts: number;
  pass_yards: number;
  pass_tds: number;
  interceptions: number;
  // Rushing
  rush_attempts: number;
  rush_yards: number;
  rush_tds: number;
  // Receiving
  targets: number;
  receptions: number;
  receiving_yards: number;
  receiving_tds: number;
  // Fantasy (half PPR)
  fantasy_points: number;
}

/**
 * A single similar player with their similarity scores.
 * Lower similarity_score = more similar to the target.
 */
export interface SimilarPlayer {
  gsis_id: string;
  name: string;
  position: string;
  first_season: number;
  draft_year: number | null;
  draft_round: number | null;
  draft_pick: number | null;
  similarity_score: number;
  euclidean_score: number | null;
  fantasy_score: number | null;
  draft_score: number | null;
  stats: AggregatedStats | null;
}

/**
 * Request body for finding similar players.
 */
export interface SimilarityRequest {
  gsis_id: string;
  mode: 'season_number' | 'age';
  max_results: number;
  through_season: number | null;
}

/**
 * Response from the similarity search.
 */
export interface SimilarityResponse {
  target_player: PlayerInfo;
  target_stats: AggregatedStats;
  target_seasons: SeasonStats[];
  similar_players: SimilarPlayer[];
  comparison_mode: string;
  comparison_range: [number | null, number | null];
}

/**
 * Response from player search endpoint.
 */
export interface PlayerSearchResponse {
  players: PlayerSummary[];
}
