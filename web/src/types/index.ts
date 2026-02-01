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
 * A single similar player with their similarity scores.
 * Lower similarity_score = more similar to the target.
 */
export interface SimilarPlayer {
  gsis_id: string;
  name: string;
  similarity_score: number;
  euclidean_score: number | null;
  fantasy_score: number | null;
  draft_score: number | null;
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
