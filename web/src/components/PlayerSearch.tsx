/**
 * PlayerSearch component - autocomplete search for players.
 *
 * Features:
 * - Text input with debounced search (waits for user to stop typing)
 * - Dropdown showing matching players
 * - Position badges (QB, RB, WR, TE)
 * - Callback when a player is selected
 */

import { useState, useEffect, useRef } from 'react';
import { usePlayerSearch } from '../hooks/usePlayerSearch';
import type { PlayerSummary } from '../types';

interface PlayerSearchProps {
  // Called when user selects a player
  onSelect: (player: PlayerSummary) => void;
  // Optional: currently selected player (for display)
  selectedPlayer?: PlayerSummary | null;
}

export function PlayerSearch({ onSelect, selectedPlayer }: PlayerSearchProps) {
  // Local state for the input value
  const [inputValue, setInputValue] = useState('');
  // Debounced value - only updates after user stops typing
  const [debouncedValue, setDebouncedValue] = useState('');
  // Whether the dropdown is open
  const [isOpen, setIsOpen] = useState(false);
  // Ref for click-outside detection
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch players based on debounced search value
  const { data, isLoading } = usePlayerSearch(debouncedValue);

  // Debounce the input value (wait 300ms after user stops typing)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(inputValue);
    }, 300);

    // Cleanup: cancel the timer if inputValue changes before 300ms
    return () => clearTimeout(timer);
  }, [inputValue]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle player selection
  const handleSelect = (player: PlayerSummary) => {
    onSelect(player);
    setInputValue(player.name); // Show selected name in input
    setIsOpen(false);
  };

  // Position badge colors
  const positionColors: Record<string, string> = {
    QB: 'bg-red-100 text-red-800',
    RB: 'bg-blue-100 text-blue-800',
    WR: 'bg-green-100 text-green-800',
    TE: 'bg-purple-100 text-purple-800',
  };

  return (
    <div ref={containerRef} className="relative">
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search for a player (e.g., 'Patrick Mahomes')"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
        />
        {/* Loading spinner */}
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-5 w-5 border-2 border-primary-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && data && data.players.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {data.players.map((player) => (
            <button
              key={player.gsis_id}
              onClick={() => handleSelect(player)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between border-b border-gray-100 last:border-b-0"
            >
              <div>
                <span className="font-medium">{player.name}</span>
                <span className="text-gray-500 text-sm ml-2">
                  {player.first_season}-{player.last_season}
                </span>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${positionColors[player.position]}`}>
                {player.position}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* No results message */}
      {isOpen && debouncedValue.length >= 2 && data && data.players.length === 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-gray-500 text-center">
          No players found for "{debouncedValue}"
        </div>
      )}

      {/* Selected Player Display */}
      {selectedPlayer && (
        <div className="mt-2 p-3 bg-primary-50 border border-primary-200 rounded-lg">
          <span className="text-sm text-primary-700">Selected: </span>
          <span className="font-medium">{selectedPlayer.name}</span>
          <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${positionColors[selectedPlayer.position]}`}>
            {selectedPlayer.position}
          </span>
          <span className="text-gray-500 text-sm ml-2">
            ({selectedPlayer.seasons_played} seasons)
          </span>
        </div>
      )}
    </div>
  );
}
