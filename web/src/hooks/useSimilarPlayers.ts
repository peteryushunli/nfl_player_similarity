/**
 * Custom React hook for finding similar players.
 *
 * This uses a mutation instead of a query because:
 * - The search is triggered explicitly by user action
 * - We don't want to automatically refetch
 * - It's a POST request with a request body
 */

import { useMutation } from '@tanstack/react-query';
import { findSimilarPlayers } from '../api/client';
import type { SimilarityRequest } from '../types';

/**
 * Hook to find similar players.
 *
 * Returns a mutation object that you can trigger with mutate() or mutateAsync().
 *
 * @example
 * function MyComponent() {
 *   const { mutate, data, isPending, error } = useSimilarPlayers();
 *
 *   const handleSearch = () => {
 *     mutate({
 *       gsis_id: '00-0033873',
 *       mode: 'season_number',
 *       max_results: 10,
 *       through_season: null
 *     });
 *   };
 *
 *   if (isPending) return <div>Finding similar players...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *
 *   return (
 *     <div>
 *       <button onClick={handleSearch}>Find Similar</button>
 *       {data && (
 *         <ul>
 *           {data.similar_players.map(player => (
 *             <li key={player.gsis_id}>{player.name}</li>
 *           ))}
 *         </ul>
 *       )}
 *     </div>
 *   );
 * }
 */
export function useSimilarPlayers() {
  return useMutation({
    // The mutationFn receives the request object and calls the API
    mutationFn: (request: SimilarityRequest) => findSimilarPlayers(request),
  });
}
