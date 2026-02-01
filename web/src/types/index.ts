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
  headshot_url: string | null;
}

/**
 * Detailed player information including draft data.
 */
export interface PlayerInfo extends PlayerSummary {
  headshot_url: string | null;
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
  // Passing
  pass_completions: number | null;
  pass_attempts: number | null;
  pass_yards: number | null;
  pass_tds: number | null;
  interceptions: number | null;
  // Rushing
  rush_attempts: number | null;
  rush_yards: number | null;
  rush_tds: number | null;
  // Receiving
  targets: number | null;
  receptions: number | null;
  receiving_yards: number | null;
  receiving_tds: number | null;
  // Fantasy
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
 * A single data point for career trajectory chart.
 */
export interface CareerDataPoint {
  season_number: number;
  season: number;  // actual year
  fantasy_points: number;  // half PPR
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
  headshot_url: string | null;
  draft_year: number | null;
  draft_round: number | null;
  draft_pick: number | null;
  draft_position_pick: number | null;  // e.g., 1st QB taken, 2nd RB taken
  similarity_score: number;
  euclidean_score: number | null;
  fantasy_score: number | null;
  draft_score: number | null;
  stats: AggregatedStats | null;
  career_data: CareerDataPoint[];  // Full career trajectory for chart
}

/**
 * Scoring format types.
 */
export type ScoringFormat = 'standard' | 'half_ppr' | 'ppr';

/**
 * Request body for finding similar players.
 */
export interface SimilarityRequest {
  gsis_id: string;
  mode: 'season_number' | 'age';
  scoring_format: ScoringFormat;
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
  target_career_data: CareerDataPoint[];  // Full career trajectory for chart
  similar_players: SimilarPlayer[];
  comparison_mode: string;
  scoring_format: ScoringFormat;
  comparison_range: [number | null, number | null];
}

/**
 * Response from player search endpoint.
 */
export interface PlayerSearchResponse {
  players: PlayerSummary[];
}
