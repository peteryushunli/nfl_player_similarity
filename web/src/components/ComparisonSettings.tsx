/**
 * ComparisonSettings component - controls for similarity search.
 *
 * Allows user to configure:
 * - Comparison mode (by season number or by age)
 * - Number of seasons to compare through
 * - Maximum number of results
 */

interface ComparisonSettingsProps {
  // Current values
  mode: 'season_number' | 'age';
  throughSeason: number | null;
  maxResults: number;
  // Max seasons available (based on selected player)
  maxSeasons: number;
  // Callbacks when values change
  onModeChange: (mode: 'season_number' | 'age') => void;
  onThroughSeasonChange: (season: number | null) => void;
  onMaxResultsChange: (max: number) => void;
}

export function ComparisonSettings({
  mode,
  throughSeason,
  maxResults,
  maxSeasons,
  onModeChange,
  onThroughSeasonChange,
  onMaxResultsChange,
}: ComparisonSettingsProps) {
  return (
    <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
      <h3 className="font-semibold text-gray-700 mb-4">Comparison Settings</h3>

      <div className="space-y-4">
        {/* Comparison Mode */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Compare By
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => onModeChange('season_number')}
              className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                mode === 'season_number'
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'
              }`}
            >
              Season Number
            </button>
            <button
              onClick={() => onModeChange('age')}
              className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                mode === 'age'
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary-400'
              }`}
            >
              Age
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {mode === 'season_number'
              ? 'Compares players through their first N seasons'
              : 'Compares players at the same ages'}
          </p>
        </div>

        {/* Through Season Slider (only for season_number mode) */}
        {mode === 'season_number' && (
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Compare Through Season: {throughSeason || maxSeasons}
            </label>
            <input
              type="range"
              min={1}
              max={maxSeasons}
              value={throughSeason || maxSeasons}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                // If set to max, use null (meaning "all seasons")
                onThroughSeasonChange(value === maxSeasons ? null : value);
              }}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>1</span>
              <span>{maxSeasons}</span>
            </div>
          </div>
        )}

        {/* Max Results */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Number of Results: {maxResults}
          </label>
          <input
            type="range"
            min={5}
            max={25}
            step={5}
            value={maxResults}
            onChange={(e) => onMaxResultsChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>5</span>
            <span>25</span>
          </div>
        </div>
      </div>
    </div>
  );
}
