/**
 * StatsTable - Displays player stats in a formatted table.
 *
 * Shows position-relevant stats (passing for QB, rushing for RB, etc.)
 */

import type { AggregatedStats } from '../types';

interface StatsTableProps {
  stats: AggregatedStats;
  position: string;
  title?: string;
}

export function StatsTable({ stats, position, title }: StatsTableProps) {
  // Determine which stats to show based on position
  const isQB = position === 'QB';
  const isRB = position === 'RB';
  const isWR = position === 'WR';
  const isTE = position === 'TE';

  const formatNumber = (n: number) => n.toLocaleString();

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      {title && (
        <h4 className="text-sm font-medium text-gray-500 mb-3">{title}</h4>
      )}

      <div className="space-y-4">
        {/* Games */}
        <div>
          <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Games</div>
          <div className="text-lg font-semibold">{stats.games_played} GP</div>
        </div>

        {/* Passing Stats (QB focused) */}
        {isQB && (
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Passing</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-600">Yards:</span>{' '}
                <span className="font-medium">{formatNumber(stats.pass_yards)}</span>
              </div>
              <div>
                <span className="text-gray-600">TDs:</span>{' '}
                <span className="font-medium">{stats.pass_tds}</span>
              </div>
              <div>
                <span className="text-gray-600">Comp:</span>{' '}
                <span className="font-medium">{stats.pass_completions}/{stats.pass_attempts}</span>
              </div>
              <div>
                <span className="text-gray-600">INTs:</span>{' '}
                <span className="font-medium">{stats.interceptions}</span>
              </div>
            </div>
          </div>
        )}

        {/* Rushing Stats (RB and QB) */}
        {(isRB || isQB) && (
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Rushing</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-600">Yards:</span>{' '}
                <span className="font-medium">{formatNumber(stats.rush_yards)}</span>
              </div>
              <div>
                <span className="text-gray-600">TDs:</span>{' '}
                <span className="font-medium">{stats.rush_tds}</span>
              </div>
              <div>
                <span className="text-gray-600">Carries:</span>{' '}
                <span className="font-medium">{stats.rush_attempts}</span>
              </div>
              {isRB && stats.rush_attempts > 0 && (
                <div>
                  <span className="text-gray-600">YPC:</span>{' '}
                  <span className="font-medium">{(stats.rush_yards / stats.rush_attempts).toFixed(1)}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Receiving Stats (WR, TE, RB) */}
        {(isWR || isTE || isRB) && (
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Receiving</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-600">Yards:</span>{' '}
                <span className="font-medium">{formatNumber(stats.receiving_yards)}</span>
              </div>
              <div>
                <span className="text-gray-600">TDs:</span>{' '}
                <span className="font-medium">{stats.receiving_tds}</span>
              </div>
              <div>
                <span className="text-gray-600">Rec:</span>{' '}
                <span className="font-medium">{stats.receptions}</span>
              </div>
              <div>
                <span className="text-gray-600">Targets:</span>{' '}
                <span className="font-medium">{stats.targets}</span>
              </div>
            </div>
          </div>
        )}

        {/* Fantasy Points */}
        <div>
          <div className="text-xs text-gray-400 uppercase tracking-wide mb-1">Fantasy (Half PPR)</div>
          <div className="text-lg font-semibold text-blue-600">
            {stats.fantasy_points.toFixed(1)} pts
          </div>
        </div>
      </div>
    </div>
  );
}
