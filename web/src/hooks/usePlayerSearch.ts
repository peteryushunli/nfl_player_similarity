/**
 * Custom React hook for searching players.
 *
 * This hook uses TanStack Query (React Query) to manage the API call state.
 * It automatically handles:
 * - Loading states
 * - Error states
 * - Caching results
 * - Deduplicating requests
 */

import { useQuery } from '@tanstack/react-query';
import { searchPlayers } from '../api/client';

/**
 * Hook to search for players by name.
 *
 * @param query - The search string (needs at least 2 characters)
 * @param position - Optional position filter
 * @returns Query result with players, loading state, and error
 *
 * @example
 * function MyComponent() {
 *   const { data, isLoading, error } = usePlayerSearch('mahomes');
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>Error!</div>;
 *
 *   return (
 *     <ul>
 *       {data?.players.map(player => (
 *         <li key={player.gsis_id}>{player.name}</li>
 *       ))}
 *     </ul>
 *   );
 * }
 */
export function usePlayerSearch(query: string, position?: string) {
  return useQuery({
    // The queryKey is used for caching - queries with the same key share data
    queryKey: ['players', 'search', query, position],

    // The queryFn is the function that fetches the data
    queryFn: () => searchPlayers(query, position),

    // Only run the query if we have at least 2 characters
    // This prevents unnecessary API calls while typing
    enabled: query.length >= 2,

    // Keep data fresh but don't refetch too aggressively
    staleTime: 30 * 1000, // Consider data fresh for 30 seconds
  });
}
