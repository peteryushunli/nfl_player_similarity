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

import { useState } from 'react';
import { PlayerSearch } from '../components/PlayerSearch';
import { ComparisonSettings } from '../components/ComparisonSettings';
import { SimilarPlayersList } from '../components/SimilarPlayersList';
import { useSimilarPlayers } from '../hooks/useSimilarPlayers';
import type { PlayerSummary } from '../types';

export function HomePage() {
  // Selected player state
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerSummary | null>(null);

  // Comparison settings state
  const [mode, setMode] = useState<'season_number' | 'age'>('season_number');
  const [throughSeason, setThroughSeason] = useState<number | null>(null);
  const [maxResults, setMaxResults] = useState(15);

  // Similar players mutation hook
  const { mutate, data, isPending, error } = useSimilarPlayers();

  // Handle finding similar players
  const handleFindSimilar = () => {
    if (!selectedPlayer) return;

    mutate({
      gsis_id: selectedPlayer.gsis_id,
      mode,
      max_results: maxResults,
      through_season: throughSeason,
    });
  };

  // Handle clicking on a similar player (future: navigate to detail page)
  const handlePlayerClick = (gsisId: string) => {
    // For now, just log it. Later, navigate to player detail page:
    // navigate(`/player/${gsisId}`);
    console.log('Clicked player:', gsisId);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Search Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          1. Select a Player
        </h2>
        <PlayerSearch
          onSelect={setSelectedPlayer}
          selectedPlayer={selectedPlayer}
        />
      </section>

      {/* Settings Section - only show if player is selected */}
      {selectedPlayer && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            2. Configure Comparison
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Settings Panel */}
            <ComparisonSettings
              mode={mode}
              throughSeason={throughSeason}
              maxResults={maxResults}
              maxSeasons={selectedPlayer.seasons_played}
              onModeChange={setMode}
              onThroughSeasonChange={setThroughSeason}
              onMaxResultsChange={setMaxResults}
            />

            {/* Player Info Card */}
            <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
              <h3 className="font-semibold text-gray-700 mb-3">Selected Player</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Name:</span>
                  <span className="font-medium">{selectedPlayer.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Position:</span>
                  <span className="font-medium">{selectedPlayer.position}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Seasons:</span>
                  <span className="font-medium">
                    {selectedPlayer.first_season} - {selectedPlayer.last_season}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Career Length:</span>
                  <span className="font-medium">{selectedPlayer.seasons_played} seasons</span>
                </div>
              </div>

              {/* Find Similar Button */}
              <button
                onClick={handleFindSimilar}
                disabled={isPending}
                className="w-full mt-4 px-4 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-primary-300 disabled:cursor-not-allowed transition-colors"
              >
                {isPending ? 'Finding...' : 'Find Similar Players'}
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Results Section */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          3. Results
        </h2>
        <SimilarPlayersList
          data={data ?? null}
          isLoading={isPending}
          error={error}
          onPlayerClick={handlePlayerClick}
        />
      </section>
    </div>
  );
}
