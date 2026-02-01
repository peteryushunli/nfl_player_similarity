/**
 * SimilarPlayerCard component - displays one similar player result.
 *
 * Shows:
 * - Player name and similarity score (prominent)
 * - Score breakdown (expandable details)
 * - Click handler for future navigation
 */

import type { SimilarPlayer } from '../types';

interface SimilarPlayerCardProps {
  player: SimilarPlayer;
  rank: number; // 1-based rank
  onClick?: () => void;
}

export function SimilarPlayerCard({ player, rank, onClick }: SimilarPlayerCardProps) {
  // Convert similarity score to a percentage (lower score = higher similarity)
  // A score of 0 = 100% similar, score of 1 = 0% similar
  const similarityPercent = Math.max(0, Math.round((1 - player.similarity_score) * 100));

  // Color based on similarity (green = very similar, yellow = somewhat, red = less)
  const getScoreColor = (score: number) => {
    if (score < 0.1) return 'text-green-600 bg-green-50';
    if (score < 0.2) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className="p-4">
        {/* Top row: rank, name, score */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Rank badge */}
            <span className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm font-bold text-gray-600">
              {rank}
            </span>
            {/* Player name */}
            <span className="font-semibold text-gray-800">{player.name}</span>
          </div>

          {/* Similarity score */}
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(player.similarity_score)}`}>
            {similarityPercent}% match
          </div>
        </div>

        {/* Score breakdown (smaller, secondary info) */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex gap-4 text-xs text-gray-500">
          {player.euclidean_score !== null && (
            <div>
              <span className="font-medium">Stats: </span>
              {player.euclidean_score.toFixed(2)}
            </div>
          )}
          {player.fantasy_score !== null && (
            <div>
              <span className="font-medium">Fantasy: </span>
              {player.fantasy_score.toFixed(2)}
            </div>
          )}
          {player.draft_score !== null && (
            <div>
              <span className="font-medium">Draft: </span>
              {(player.draft_score * 100).toFixed(0)}%
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
