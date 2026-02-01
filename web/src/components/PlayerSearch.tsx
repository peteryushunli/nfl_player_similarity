/**
 * PlayerSearch component - autocomplete search for players.
 *
 * Features:
 * - Text input with search icon and debounced search
 * - Dropdown showing matching players
 * - Solid color position badges (QB=red, RB=blue, WR=green, TE=purple)
 * - Callback when a player is selected
 */

import { useState, useEffect, useRef } from 'react';
import { usePlayerSearch } from '../hooks/usePlayerSearch';
import type { PlayerSummary } from '../types';

interface PlayerSearchProps {
  onSelect: (player: PlayerSummary) => void;
  selectedPlayer?: PlayerSummary | null;
}

// Position badge colors - solid colors for high contrast
const positionColors: Record<string, string> = {
  QB: 'bg-red-600 text-white',
  RB: 'bg-blue-600 text-white',
  WR: 'bg-green-600 text-white',
  TE: 'bg-purple-600 text-white',
};

export function PlayerSearch({ onSelect, selectedPlayer }: PlayerSearchProps) {
  const [inputValue, setInputValue] = useState('');
  const [debouncedValue, setDebouncedValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data, isLoading } = usePlayerSearch(debouncedValue);

  // Debounce the input value
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(inputValue);
    }, 300);
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

  const handleSelect = (player: PlayerSummary) => {
    onSelect(player);
    setInputValue(player.name);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className="relative">
      {/* Search Input with Icon */}
      <div className="relative">
        {/* Search Icon */}
        <svg
          className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => {
            setInputValue(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search for a player (e.g., 'Patrick Mahomes')"
          className="w-full pl-12 pr-12 py-4 text-lg border-2 border-slate-200 rounded-xl shadow-sm
            focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 outline-none
            transition-all duration-200 placeholder:text-slate-400"
        />
        {/* Loading spinner */}
        {isLoading && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && data && data.players.length > 0 && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl max-h-72 overflow-auto">
          {data.players.map((player) => (
            <button
              key={player.gsis_id}
              onClick={() => handleSelect(player)}
              className="w-full px-4 py-3 text-left hover:bg-slate-50 flex items-center justify-between
                border-b border-slate-100 last:border-b-0 transition-colors"
            >
              <div>
                <span className="font-semibold text-slate-900">{player.name}</span>
                <span className="text-slate-500 text-sm ml-2">
                  {player.first_season}–{player.last_season}
                </span>
              </div>
              <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${positionColors[player.position]}`}>
                {player.position}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* No results message */}
      {isOpen && debouncedValue.length >= 2 && data && data.players.length === 0 && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl p-4 text-slate-500 text-center">
          No players found for "{debouncedValue}"
        </div>
      )}

      {/* Selected Player Display */}
      {selectedPlayer && (
        <div className="mt-3 p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-3">
          <span className={`px-3 py-1.5 rounded-lg text-sm font-bold ${positionColors[selectedPlayer.position]}`}>
            {selectedPlayer.position}
          </span>
          <div>
            <span className="font-bold text-slate-900">{selectedPlayer.name}</span>
            <span className="text-slate-500 text-sm ml-2">
              {selectedPlayer.first_season}–{selectedPlayer.last_season} • {selectedPlayer.seasons_played} seasons
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
