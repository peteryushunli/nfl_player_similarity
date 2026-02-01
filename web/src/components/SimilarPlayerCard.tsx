/**
 * SimilarPlayerCard component - displays one similar player result.
 *
 * Features:
 * - Large rank number with accent color
 * - Left accent border
 * - Similarity percentage with color coding
 * - Stats comparison table
 */

import type { SimilarPlayer, AggregatedStats } from '../types';
import { StatsComparisonTable } from './StatsComparisonTable';

interface SimilarPlayerCardProps {
  player: SimilarPlayer;
  targetStats: AggregatedStats;
  targetName: string;
  targetPosition: string;
  rank: number;
  onClick?: () => void;
}

// Position badge colors
const positionColors: Record<string, string> = {
  QB: 'bg-red-600 text-white',
  RB: 'bg-blue-600 text-white',
  WR: 'bg-green-600 text-white',
  TE: 'bg-purple-600 text-white',
};

function formatDraft(round: number | null, pick: number | null): string {
  if (!round || !pick) return 'Undrafted';
  return `Rd ${round}, Pick ${pick}`;
}

export function SimilarPlayerCard({
  player,
  targetStats,
  targetName,
  targetPosition,
  rank,
  onClick,
}: SimilarPlayerCardProps) {
  const similarityPercent = Math.max(0, Math.round((1 - player.similarity_score) * 100));

  // Similarity score color coding
  const getScoreStyle = (score: number) => {
    if (score < 0.1) return 'bg-green-500 text-white';
    if (score < 0.2) return 'bg-yellow-500 text-white';
    return 'bg-orange-500 text-white';
  };

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden
        border-l-4 border-l-blue-500 ${
        onClick ? 'cursor-pointer hover:shadow-xl transition-shadow' : ''
      }`}
    >
      {/* Header */}
      <div className="px-5 py-4 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Large rank number */}
            <span className="text-4xl font-black text-blue-600">
              #{rank}
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-lg font-bold text-slate-900">{player.name}</h4>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${positionColors[player.position] || 'bg-slate-600 text-white'}`}>
                  {player.position}
                </span>
              </div>
              <p className="text-sm text-slate-500">
                {player.first_season} • {formatDraft(player.draft_round, player.draft_pick)}
              </p>
            </div>
          </div>
          {/* Similarity score */}
          <div className={`px-4 py-2 rounded-lg text-lg font-bold ${getScoreStyle(player.similarity_score)}`}>
            {similarityPercent}%
          </div>
        </div>
      </div>

      {/* Stats Table */}
      {player.stats && (
        <div className="p-4">
          <StatsComparisonTable
            targetStats={targetStats}
            compStats={player.stats}
            targetName={targetName}
            compName={player.name}
            position={targetPosition}
          />
        </div>
      )}
    </div>
  );
}
