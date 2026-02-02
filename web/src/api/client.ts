/**
 * API client for communicating with the FastAPI backend.
 *
 * This module sets up axios (a popular HTTP client library) and provides
 * functions to call our API endpoints.
 *
 * Why use a separate API client?
 * - Single place to configure the base URL
 * - Easy to add authentication headers later
 * - Type-safe request/response handling
 */

import axios from 'axios';
import type {
  PlayerSearchResponse,
  PlayerInfo,
  SimilarityRequest,
  SimilarityResponse,
} from '../types';

// Create an axios instance with the API base URL
// During development, the API runs on port 8000
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Search for players by name.
 *
 * @param query - Search string (minimum 2 characters)
 * @param position - Optional position filter (QB, RB, WR, TE)
 * @returns Promise with list of matching players
 *
 * @example
 * const results = await searchPlayers('mahomes');
 * // results.players = [{ gsis_id: '...', name: 'Patrick Mahomes', ... }]
 */
export async function searchPlayers(
  query: string,
  position?: string
): Promise<PlayerSearchResponse> {
  // Build the query parameters
  const params: Record<string, string> = { q: query };
  if (position) {
    params.position = position;
  }

  // Make the GET request
  const response = await api.get<PlayerSearchResponse>('/players/search', { params });
  return response.data;
}

/**
 * Get detailed information about a specific player.
 *
 * @param gsisId - The player's GSIS ID (e.g., '00-0033873')
 * @returns Promise with player details including draft info
 */
export async function getPlayer(gsisId: string): Promise<PlayerInfo> {
  const response = await api.get<PlayerInfo>(`/players/${gsisId}`);
  return response.data;
}

/**
 * Find players similar to the target player.
 *
 * @param request - The similarity search parameters
 * @returns Promise with similar players and their scores
 *
 * @example
 * const results = await findSimilarPlayers({
 *   gsis_id: '00-0033873',
 *   mode: 'season_number',
 *   max_results: 10,
 *   through_season: 5
 * });
 */
export async function findSimilarPlayers(
  request: SimilarityRequest
): Promise<SimilarityResponse> {
  // POST request with JSON body
  const response = await api.post<SimilarityResponse>('/similarity/find', request);
  return response.data;
}

// Export the axios instance in case we need direct access
export default api;
