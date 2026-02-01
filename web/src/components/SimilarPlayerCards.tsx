/**
 * SimilarPlayerCards - Horizontal cards showing similarity score breakdown.
 *
 * Features:
 * - Horizontal layout with 5 cards
 * - Player headshots with fallback to initials
 * - Shows overall similarity, fantasy score, draft score breakdown
 * - Color-coded by similarity level
 * - Compact but informative
 */

import type { SimilarPlayer } from '../types';
import { PlayerHeadshot } from './PlayerHeadshot';

interface SimilarPlayerCardsProps {
  players: SimilarPlayer[];
  targetPosition: string;
  onPlayerClick?: (gsisId: string) => void;
}

// Position badge colors
const positionColors: Record<string, string> = {
  QB: 'bg-red-600 text-white',
  RB: 'bg-blue-600 text-white',
  WR: 'bg-green-600 text-white',
  TE: 'bg-purple-600 text-white',
};

// Color palette for player cards (matches chart colors)
const CARD_COLORS = [
  { bg: 'bg-blue-50', border: 'border-blue-400', accent: 'text-blue-600' },
  { bg: 'bg-emerald-50', border: 'border-emerald-400', accent: 'text-emerald-600' },
  { bg: 'bg-amber-50', border: 'border-amber-400', accent: 'text-amber-600' },
  { bg: 'bg-violet-50', border: 'border-violet-400', accent: 'text-violet-600' },
  { bg: 'bg-pink-50', border: 'border-pink-400', accent: 'text-pink-600' },
];

function formatDraft(round: number | null, pick: number | null, positionPick: number | null, position: string): string {
  if (!round || !pick) return 'UDFA';
  if (positionPick) {
    return `Rd ${round} (${position}${positionPick})`;
  }
  return `Rd ${round}, #${pick}`;
}

// Convert similarity score (0 = identical, higher = less similar) to percentage
function scoreToPercent(score: number): number {
  return Math.max(0, Math.round((1 - score) * 100));
}

export function SimilarPlayerCards({ players, onPlayerClick }: SimilarPlayerCardsProps) {
  const top5 = players.slice(0, 5);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-md p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-1.5 h-8 bg-blue-500 rounded-full" />
        <h3 className="text-xl font-bold text-slate-800">Top 5 Similar Players</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {top5.map((player, idx) => {
          const colors = CARD_COLORS[idx];
          const similarityPct = scoreToPercent(player.similarity_score);
          const fantasyPct = player.fantasy_score !== null ? scoreToPercent(player.fantasy_score) : null;
          const draftPct = player.draft_score !== null ? Math.round(player.draft_score * 100) : null;

          return (
            <div
              key={player.gsis_id}
              onClick={() => onPlayerClick?.(player.gsis_id)}
              className={`${colors.bg} rounded-lg border-2 ${colors.border} p-4 transition-transform hover:scale-[1.02] ${
                onPlayerClick ? 'cursor-pointer' : ''
              }`}
            >
              {/* Header with rank, headshot, and position */}
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xl font-black ${colors.accent}`}>#{idx + 1}</span>
                <PlayerHeadshot headshotUrl={player.headshot_url} name={player.name} size="sm" />
                <span className={`ml-auto px-2 py-0.5 rounded text-xs font-bold ${positionColors[player.position] || 'bg-slate-600 text-white'}`}>
                  {player.position}
                </span>
              </div>

              {/* Player name */}
              <h4 className="font-bold text-slate-900 text-sm truncate" title={player.name}>
                {player.name}
              </h4>

              {/* Draft and year info */}
              <p className="text-xs text-slate-500 mb-3">
                {player.first_season} • {formatDraft(player.draft_round, player.draft_pick, player.draft_position_pick, player.position)}
              </p>

              {/* Similarity score - large and prominent */}
              <div className="bg-white rounded-lg p-2 mb-2 text-center border border-slate-200">
                <div className={`text-2xl font-black ${colors.accent}`}>
                  {similarityPct}%
                </div>
                <div className="text-[10px] uppercase tracking-wide text-slate-500 font-medium">
                  Overall Match
                </div>
              </div>

              {/* Score breakdown */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                {fantasyPct !== null && (
                  <div className="bg-white/50 rounded p-1.5 text-center">
                    <div className="font-bold text-slate-700">{fantasyPct}%</div>
                    <div className="text-[9px] text-slate-500 uppercase">Fantasy</div>
                  </div>
                )}
                {draftPct !== null && (
                  <div className="bg-white/50 rounded p-1.5 text-center">
                    <div className="font-bold text-slate-700">{draftPct}%</div>
                    <div className="text-[9px] text-slate-500 uppercase">Draft</div>
                  </div>
                )}
              </div>

              {/* Career stats summary */}
              {player.stats && (
                <div className="mt-2 pt-2 border-t border-slate-300/50">
                  <div className="flex justify-between text-[10px] text-slate-600">
                    <span>{player.stats.games_played} G</span>
                    <span>{player.stats.fantasy_points.toFixed(0)} FP</span>
                  </div>
                </div>
              )}

              {/* Click hint */}
              {onPlayerClick && (
                <div className="mt-2 text-center">
                  <span className="text-[9px] text-slate-400 uppercase tracking-wide">
                    Click for details
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
