/**
 * HomePage - the main page of the application.
 *
 * This is where users:
 * 1. Search for a player
 * 2. Configure comparison settings
 * 3. Find and view similar players
 *
 * State management:
 * - selectedPlayer: The player to find similarities for
 * - Comparison settings: mode, throughSeason, maxResults
 * - useSimilarPlayers hook manages the API call state
 */

import { useState, useRef } from 'react';
import { PlayerSearch } from '../components/PlayerSearch';
import { ComparisonSettings } from '../components/ComparisonSettings';
import { SimilarPlayersList } from '../components/SimilarPlayersList';
import { useSimilarPlayers } from '../hooks/useSimilarPlayers';
import type { PlayerSummary } from '../types';

export function HomePage() {
  // Ref for scrolling to top
  const searchRef = useRef<HTMLDivElement>(null);

  // Selected player state
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerSummary | null>(null);

  // Comparison settings state
  const [mode, setMode] = useState<'season_number' | 'age'>('season_number');
  const [throughSeason, setThroughSeason] = useState<number | null>(null);

  // Similar players mutation hook
  const { mutate, data, isPending, error, reset } = useSimilarPlayers();

  // Handle finding similar players
  const handleFindSimilar = () => {
    if (!selectedPlayer) return;

    mutate({
      gsis_id: selectedPlayer.gsis_id,
      mode,
      max_results: 10, // Request more than we display in case of filtering
      through_season: throughSeason,
    });
  };

  // Handle clicking on a similar player (future: navigate to detail page)
  const handlePlayerClick = (gsisId: string) => {
    // For now, just log it. Later, navigate to player detail page:
    // navigate(`/player/${gsisId}`);
    console.log('Clicked player:', gsisId);
  };

  // Handle starting a new comparison
  const handleNewComparison = () => {
    setSelectedPlayer(null);
    setThroughSeason(null);
    reset(); // Clear previous results
    // Scroll to top
    searchRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Check if we have results to show
  const hasResults = data && data.similar_players.length > 0;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search Section */}
      <section ref={searchRef} className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          1. Select a Player
        </h2>
        <PlayerSearch
          onSelect={setSelectedPlayer}
          selectedPlayer={selectedPlayer}
        />
      </section>

      {/* Settings Section - only show if player is selected and no results yet */}
      {selectedPlayer && !hasResults && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            2. Configure Comparison
          </h2>
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            {/* Player header */}
            <div className="mb-6 pb-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800">{selectedPlayer.name}</h3>
              <p className="text-sm text-gray-500">
                {selectedPlayer.position} | {selectedPlayer.first_season} - {selectedPlayer.last_season} ({selectedPlayer.seasons_played} seasons)
              </p>
            </div>

            {/* Settings */}
            <ComparisonSettings
              mode={mode}
              throughSeason={throughSeason}
              maxSeasons={selectedPlayer.seasons_played}
              onModeChange={setMode}
              onThroughSeasonChange={setThroughSeason}
            />

            {/* Find Similar Button */}
            <button
              onClick={handleFindSimilar}
              disabled={isPending}
              className="w-full mt-6 px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
            >
              {isPending ? 'Finding...' : 'Find Similar Players'}
            </button>
          </div>
        </section>
      )}

      {/* Results Section - only show if we have data or are loading */}
      {(isPending || hasResults || error) && (
        <section>
          <SimilarPlayersList
            data={data ?? null}
            isLoading={isPending}
            error={error}
            onPlayerClick={handlePlayerClick}
            onNewComparison={handleNewComparison}
          />
        </section>
      )}
    </div>
  );
}
