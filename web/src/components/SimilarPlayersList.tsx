/**
 * SimilarPlayersList component - displays the list of similar players.
 *
 * Features:
 * - Loading state with spinner
 * - Target player card with season-by-season stats table
 * - Section titles with accent bar
 * - Horizontal player summary cards that link to detailed views
 * - Foldable detailed comparisons section
 */

import { useState, useRef, useEffect } from 'react';
import type { SimilarityResponse } from '../types';
import { SimilarPlayerCard } from './SimilarPlayerCard';
import { PlayerSeasonTable } from './PlayerSeasonTable';
import { SimilarPlayerCards } from './SimilarPlayerCards';
import { CareerTrajectoryChart } from './CareerTrajectoryChart';
import { PlayerHeadshot } from './PlayerHeadshot';

interface SimilarPlayersListProps {
  data: SimilarityResponse | null;
  isLoading: boolean;
  error: Error | null;
  onPlayerClick?: (gsisId: string) => void;
  onNewComparison?: () => void;
}

// Position badge colors
const positionColors: Record<string, string> = {
  QB: 'bg-red-600 text-white',
  RB: 'bg-blue-600 text-white',
  WR: 'bg-green-600 text-white',
  TE: 'bg-purple-600 text-white',
};

const MAX_RESULTS = 5;

export function SimilarPlayersList({
  data,
  isLoading,
  error,
  onPlayerClick,
  onNewComparison,
}: SimilarPlayersListProps) {
  const [isDetailedOpen, setIsDetailedOpen] = useState(false);
  const [highlightedPlayerId, setHighlightedPlayerId] = useState<string | null>(null);
  const detailedRefs = useRef<Record<string, HTMLDivElement | null>>({});

  // Scroll to a specific player's detailed card
  const scrollToPlayer = (gsisId: string) => {
    // Open the detailed section if closed
    if (!isDetailedOpen) {
      setIsDetailedOpen(true);
    }
    setHighlightedPlayerId(gsisId);

    // Wait for the section to open, then scroll
    setTimeout(() => {
      const element = detailedRefs.current[gsisId];
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  // Clear highlight after animation
  useEffect(() => {
    if (highlightedPlayerId) {
      const timer = setTimeout(() => setHighlightedPlayerId(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [highlightedPlayerId]);

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-md p-12 text-center">
        <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-slate-600 font-medium">Finding similar players...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 rounded-xl border border-red-200 p-8 text-center">
        <p className="text-red-600 font-bold">Error finding similar players</p>
        <p className="text-red-500 text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  // No data yet
  if (!data) {
    return (
      <div className="bg-slate-50 rounded-xl border-2 border-slate-200 border-dashed p-12 text-center">
        <svg className="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p className="text-slate-600 font-medium">
          Select a player and click "Find Similar Players" to see results
        </p>
      </div>
    );
  }

  // No similar players found
  if (data.similar_players.length === 0) {
    return (
      <div className="bg-amber-50 rounded-xl border border-amber-200 p-8 text-center">
        <p className="text-amber-700 font-bold">No similar players found</p>
        <p className="text-amber-600 text-sm mt-1">
          Try adjusting the comparison settings
        </p>
      </div>
    );
  }

  const displayedPlayers = data.similar_players.slice(0, MAX_RESULTS);
  const targetPosition = data.target_player.position;

  const comparisonDesc =
    data.comparison_mode === 'season_number'
      ? `First ${data.comparison_range[1]} season${data.comparison_range[1] !== 1 ? 's' : ''}`
      : `Ages ${data.comparison_range[0]}–${data.comparison_range[1]}`;

  const draftInfo = data.target_player.draft_round
    ? `Rd ${data.target_player.draft_round}, Pick ${data.target_player.draft_pick}${
        data.target_player.draft_position_pick
          ? ` (${targetPosition}${data.target_player.draft_position_pick})`
          : ''
      }`
    : 'Undrafted';

  return (
    <div className="space-y-10">
      {/* Target player section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden">
        {/* Player header */}
        <div className="px-5 py-4 bg-gradient-to-r from-slate-800 to-slate-700 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <PlayerHeadshot headshotUrl={data.target_player.headshot_url} name={data.target_player.name} size="lg" />
              <span className={`px-3 py-1.5 rounded-lg text-sm font-bold ${positionColors[targetPosition]}`}>
                {targetPosition}
              </span>
              <div>
                <h2 className="text-xl font-bold">
                  {data.target_player.name}
                </h2>
                <p className="text-slate-300 text-sm">
                  {data.target_player.first_season}–{data.target_player.last_season} • {draftInfo}
                </p>
              </div>
            </div>
            <div className="bg-blue-500 px-4 py-2 rounded-lg">
              <span className="text-sm font-bold">{comparisonDesc}</span>
            </div>
          </div>
        </div>

        {/* Season-by-season stats table */}
        <div className="p-4">
          <PlayerSeasonTable
            seasons={data.target_seasons}
            totals={data.target_stats}
            position={targetPosition}
          />
        </div>

        {/* New Comparison button - easy access */}
        {onNewComparison && (
          <div className="px-4 pb-4">
            <button
              onClick={onNewComparison}
              className="w-full px-4 py-3 text-sm font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200"
            >
              ← Start New Comparison
            </button>
          </div>
        )}
      </div>

      {/* Horizontal similar player cards */}
      <SimilarPlayerCards
        players={displayedPlayers}
        targetPosition={targetPosition}
        onPlayerClick={scrollToPlayer}
      />

      {/* Career trajectory chart */}
      <CareerTrajectoryChart
        targetName={data.target_player.name}
        targetCareerData={data.target_career_data}
        similarPlayers={displayedPlayers}
        comparisonEndSeason={data.comparison_range[1] || data.target_seasons.length}
      />

      {/* Detailed player cards section - foldable */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden">
        {/* Foldable header */}
        <button
          onClick={() => setIsDetailedOpen(!isDetailedOpen)}
          className="w-full px-5 py-4 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-1.5 h-8 bg-blue-500 rounded-full" />
            <h3 className="text-xl font-bold text-slate-800">
              Detailed Comparisons
            </h3>
            <span className="text-sm text-slate-500">
              ({displayedPlayers.length} players)
            </span>
          </div>
          <svg
            className={`w-6 h-6 text-slate-500 transition-transform duration-200 ${
              isDetailedOpen ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Collapsible content */}
        <div
          className={`transition-all duration-300 ease-in-out overflow-hidden ${
            isDetailedOpen ? 'max-h-[10000px] opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="p-5 space-y-5">
            {displayedPlayers.map((player, index) => (
              <div
                key={player.gsis_id}
                ref={(el) => { detailedRefs.current[player.gsis_id] = el; }}
                className={`transition-all duration-500 ${
                  highlightedPlayerId === player.gsis_id
                    ? 'ring-4 ring-blue-400 ring-offset-2 rounded-xl'
                    : ''
                }`}
              >
                <SimilarPlayerCard
                  player={player}
                  targetStats={data.target_stats}
                  targetName={data.target_player.name}
                  targetPosition={targetPosition}
                  rank={index + 1}
                  onClick={onPlayerClick ? () => onPlayerClick(player.gsis_id) : undefined}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* New Comparison button at bottom */}
      {onNewComparison && (
        <div className="text-center pt-4">
          <button
            onClick={onNewComparison}
            className="px-8 py-3 text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            Start New Comparison
          </button>
        </div>
      )}
    </div>
  );
}
