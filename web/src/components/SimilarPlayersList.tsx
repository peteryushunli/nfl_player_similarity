/**
 * SimilarPlayersList component - displays the list of similar players.
 *
 * Shows:
 * - Loading state
 * - Error state
 * - List of SimilarPlayerCards
 * - Metadata about the comparison
 */

import type { SimilarityResponse } from '../types';
import { SimilarPlayerCard } from './SimilarPlayerCard';

interface SimilarPlayersListProps {
  // Data from the similarity search
  data: SimilarityResponse | null;
  // Loading state
  isLoading: boolean;
  // Error state
  error: Error | null;
  // Callback when a player card is clicked
  onPlayerClick?: (gsisId: string) => void;
}

export function SimilarPlayersList({
  data,
  isLoading,
  error,
  onPlayerClick,
}: SimilarPlayersListProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">Finding similar players...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 rounded-lg border border-red-200 p-8 text-center">
        <p className="text-red-600 font-medium">Error finding similar players</p>
        <p className="text-red-500 text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  // No data yet (before first search)
  if (!data) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 border-dashed p-8 text-center">
        <p className="text-gray-500">
          Select a player and click "Find Similar Players" to see results
        </p>
      </div>
    );
  }

  // No similar players found
  if (data.similar_players.length === 0) {
    return (
      <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-8 text-center">
        <p className="text-yellow-700">No similar players found</p>
        <p className="text-yellow-600 text-sm mt-1">
          Try adjusting the comparison settings
        </p>
      </div>
    );
  }

  // Show results
  return (
    <div>
      {/* Results header with metadata */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">
          Similar Players to {data.target_player.name}
        </h2>
        <span className="text-sm text-gray-500">
          Compared {data.comparison_mode === 'season_number' ? 'seasons' : 'ages'}{' '}
          {data.comparison_range[0]} - {data.comparison_range[1]}
        </span>
      </div>

      {/* List of similar players */}
      <div className="space-y-3">
        {data.similar_players.map((player, index) => (
          <SimilarPlayerCard
            key={player.gsis_id}
            player={player}
            rank={index + 1}
            onClick={onPlayerClick ? () => onPlayerClick(player.gsis_id) : undefined}
          />
        ))}
      </div>
    </div>
  );
}
