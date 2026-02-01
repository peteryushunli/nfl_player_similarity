/**
 * ComparisonSettings component - controls for similarity search.
 *
 * Features:
 * - Pill-style toggle buttons for comparison mode
 * - Pill-style toggle buttons for scoring format
 * - Styled range slider for season/age selection
 * - Card container with shadow
 */

import type { ScoringFormat } from '../types';

interface ComparisonSettingsProps {
  mode: 'season_number' | 'age';
  scoringFormat: ScoringFormat;
  throughSeason: number | null;
  maxSeasons: number;
  onModeChange: (mode: 'season_number' | 'age') => void;
  onScoringFormatChange: (format: ScoringFormat) => void;
  onThroughSeasonChange: (season: number | null) => void;
}

export function ComparisonSettings({
  mode,
  scoringFormat,
  throughSeason,
  maxSeasons,
  onModeChange,
  onScoringFormatChange,
  onThroughSeasonChange,
}: ComparisonSettingsProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-md p-6 space-y-6">
      {/* Comparison Mode */}
      <div>
        <label className="block text-sm font-bold text-slate-700 mb-3">
          Compare By
        </label>
        <div className="inline-flex bg-slate-100 rounded-lg p-1">
          <button
            onClick={() => onModeChange('season_number')}
            className={`px-5 py-2.5 rounded-md text-sm font-semibold transition-all ${
              mode === 'season_number'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Season Number
          </button>
          <button
            onClick={() => onModeChange('age')}
            className={`px-5 py-2.5 rounded-md text-sm font-semibold transition-all ${
              mode === 'age'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Age
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          {mode === 'season_number'
            ? 'Compares players through their first N seasons'
            : 'Compares players at the same ages'}
        </p>
      </div>

      {/* Scoring Format */}
      <div>
        <label className="block text-sm font-bold text-slate-700 mb-3">
          Scoring Format
        </label>
        <div className="inline-flex bg-slate-100 rounded-lg p-1">
          <button
            onClick={() => onScoringFormatChange('standard')}
            className={`px-4 py-2.5 rounded-md text-sm font-semibold transition-all ${
              scoringFormat === 'standard'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Standard
          </button>
          <button
            onClick={() => onScoringFormatChange('half_ppr')}
            className={`px-4 py-2.5 rounded-md text-sm font-semibold transition-all ${
              scoringFormat === 'half_ppr'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Half PPR
          </button>
          <button
            onClick={() => onScoringFormatChange('ppr')}
            className={`px-4 py-2.5 rounded-md text-sm font-semibold transition-all ${
              scoringFormat === 'ppr'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Full PPR
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          {scoringFormat === 'standard' && 'No points per reception'}
          {scoringFormat === 'half_ppr' && '0.5 points per reception'}
          {scoringFormat === 'ppr' && '1.0 points per reception'}
        </p>
      </div>

      {/* Through Season Slider */}
      {mode === 'season_number' && (
        <div>
          <label className="block text-sm font-bold text-slate-700 mb-3">
            Compare Through Season
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min={1}
              max={maxSeasons}
              value={throughSeason || maxSeasons}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                onThroughSeasonChange(value === maxSeasons ? null : value);
              }}
              className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
                [&::-webkit-slider-thumb]:bg-blue-600 [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-md
                [&::-moz-range-thumb]:w-5 [&::-moz-range-thumb]:h-5
                [&::-moz-range-thumb]:bg-blue-600 [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0"
            />
            <span className="min-w-[100px] text-center py-2 px-3 bg-blue-500 text-white font-bold rounded-lg text-sm">
              {throughSeason || maxSeasons} season{(throughSeason || maxSeasons) !== 1 ? 's' : ''}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Find players with similar production in their first {throughSeason || maxSeasons} season{(throughSeason || maxSeasons) !== 1 ? 's' : ''}
          </p>
        </div>
      )}

      {/* Age mode info */}
      {mode === 'age' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-700">
            <span className="font-medium">Age mode:</span> Compares players at the same ages in their careers.
            This is useful for comparing players who entered the league at different ages.
          </p>
        </div>
      )}
    </div>
  );
}
