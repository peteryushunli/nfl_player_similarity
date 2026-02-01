/**
 * PlayerSeasonTable - Sports media-style season-by-season stats table.
 *
 * Features:
 * - Dark headers with white text
 * - Heatmap coloring based on percentile (using inline styles for reliability)
 * - Dark totals row
 * - Monospace numbers for alignment
 */

import type { SeasonStats, AggregatedStats } from '../types';
import React from 'react';

interface PlayerSeasonTableProps {
  seasons: SeasonStats[];
  totals: AggregatedStats;
  position: string;
}

/**
 * Get inline style for heatmap coloring based on percentile.
 * Using inline styles instead of Tailwind classes for reliable rendering.
 */
function getHeatmapStyle(percentile: number | null | undefined): React.CSSProperties {
  if (percentile === null || percentile === undefined) return {};

  if (percentile >= 90) return { backgroundColor: '#22c55e', color: 'white' }; // green-500
  if (percentile >= 80) return { backgroundColor: '#4ade80' }; // green-400
  if (percentile >= 70) return { backgroundColor: '#86efac' }; // green-300
  if (percentile >= 60) return { backgroundColor: '#bbf7d0' }; // green-200
  if (percentile >= 50) return { backgroundColor: '#dcfce7' }; // green-100
  if (percentile >= 40) return { backgroundColor: '#fef9c3' }; // yellow-100
  if (percentile >= 30) return { backgroundColor: '#ffedd5' }; // orange-100
  if (percentile >= 20) return { backgroundColor: '#fed7aa' }; // orange-200
  if (percentile >= 10) return { backgroundColor: '#fecaca' }; // red-200
  return { backgroundColor: '#fca5a5' }; // red-300
}

export function PlayerSeasonTable({
  seasons,
  totals,
  position,
}: PlayerSeasonTableProps) {
  const isQB = position === 'QB';
  const isRB = position === 'RB';
  const isWR = position === 'WR' || position === 'TE';

  // Format number with commas
  const fmt = (n: number) => n.toLocaleString();

  // Calculate completion percentage
  const compPct = (comp: number, att: number) => {
    if (att === 0) return '—';
    return ((comp / att) * 100).toFixed(1);
  };

  // Calculate yards per attempt
  const ypa = (yards: number, att: number) => {
    if (att === 0) return '—';
    return (yards / att).toFixed(1);
  };

  // Helper to render a stat cell with optional heatmap coloring
  const StatCell = ({
    value,
    percentile,
    format = 'number'
  }: {
    value: number | string;
    percentile?: number | null;
    format?: 'number' | 'decimal' | 'raw';
  }) => {
    const heatStyle = getHeatmapStyle(percentile);
    let displayValue: string;

    if (format === 'raw' || typeof value === 'string') {
      displayValue = String(value);
    } else if (format === 'decimal') {
      displayValue = (value as number).toFixed(1);
    } else {
      displayValue = fmt(value as number);
    }

    return (
      <td
        className="px-3 py-2 text-center font-mono"
        style={heatStyle}
      >
        {displayValue}
      </td>
    );
  };

  // Common header cell styling
  const thClass = "px-3 py-3 text-center text-xs font-bold uppercase tracking-wider";

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="w-full text-sm">
        <thead className="bg-slate-800 text-white sticky top-0">
          <tr>
            <th className={`${thClass} text-left`}>Season</th>
            <th className={thClass}>Age</th>
            <th className={thClass}>G</th>
            {isQB && (
              <>
                <th className={thClass}>Cmp</th>
                <th className={thClass}>Att</th>
                <th className={thClass}>Cmp%</th>
                <th className={thClass}>Yds</th>
                <th className={thClass}>TD</th>
                <th className={thClass}>INT</th>
                <th className={thClass}>Y/A</th>
              </>
            )}
            {(isQB || isRB) && (
              <>
                <th className={thClass}>Rush</th>
                <th className={thClass}>RuYds</th>
                <th className={thClass}>RuTD</th>
              </>
            )}
            {(isRB || isWR) && (
              <>
                <th className={thClass}>Tgt</th>
                <th className={thClass}>Rec</th>
                <th className={thClass}>RecYds</th>
                <th className={thClass}>RecTD</th>
              </>
            )}
            <th className={thClass}>Fantasy</th>
            <th className={thClass}>Pos</th>
            <th className={thClass}>Ovr</th>
          </tr>
        </thead>
        <tbody className="bg-white">
          {seasons.map((season, idx) => {
            const p = season.percentiles;
            return (
              <tr
                key={season.season}
                className={`border-b border-slate-200 hover:bg-slate-100 transition-colors ${
                  idx % 2 === 1 ? 'bg-slate-50' : ''
                }`}
              >
                <td className="px-3 py-2 text-slate-900 font-semibold">{season.season}</td>
                <td className="px-3 py-2 text-center text-slate-600 font-mono">{season.age ?? '—'}</td>
                <StatCell value={season.games_played} percentile={p?.games_played} />
                {isQB && (
                  <>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">{fmt(season.pass_completions)}</td>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">{fmt(season.pass_attempts)}</td>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">
                      {compPct(season.pass_completions, season.pass_attempts)}
                    </td>
                    <StatCell value={season.pass_yards} percentile={p?.pass_yards} />
                    <StatCell value={season.pass_tds} percentile={p?.pass_tds} />
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">{season.interceptions}</td>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">
                      {ypa(season.pass_yards, season.pass_attempts)}
                    </td>
                  </>
                )}
                {(isQB || isRB) && (
                  <>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">{season.rush_attempts}</td>
                    <StatCell value={season.rush_yards} percentile={p?.rush_yards} />
                    <StatCell value={season.rush_tds} percentile={p?.rush_tds} />
                  </>
                )}
                {(isRB || isWR) && (
                  <>
                    <td className="px-3 py-2 text-center text-slate-700 font-mono">{season.targets}</td>
                    <StatCell value={season.receptions} percentile={p?.receptions} />
                    <StatCell value={season.receiving_yards} percentile={p?.receiving_yards} />
                    <StatCell value={season.receiving_tds} percentile={p?.receiving_tds} />
                  </>
                )}
                <StatCell value={season.fantasy_points} percentile={p?.fantasy_points} format="decimal" />
                <td className="px-3 py-2 text-center text-slate-700 font-mono font-semibold">
                  {season.fantasy_position_rank ?? '—'}
                </td>
                <td className="px-3 py-2 text-center text-slate-700 font-mono">
                  {season.fantasy_overall_rank ?? '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr className="bg-slate-900 text-white font-bold">
            <td className="px-3 py-3">{seasons.length} Yrs</td>
            <td className="px-3 py-3 text-center">—</td>
            <td className="px-3 py-3 text-center font-mono">{totals.games_played}</td>
            {isQB && (
              <>
                <td className="px-3 py-3 text-center font-mono">{fmt(totals.pass_completions)}</td>
                <td className="px-3 py-3 text-center font-mono">{fmt(totals.pass_attempts)}</td>
                <td className="px-3 py-3 text-center font-mono">
                  {compPct(totals.pass_completions, totals.pass_attempts)}
                </td>
                <td className="px-3 py-3 text-center font-mono">{fmt(totals.pass_yards)}</td>
                <td className="px-3 py-3 text-center font-mono">{totals.pass_tds}</td>
                <td className="px-3 py-3 text-center font-mono">{totals.interceptions}</td>
                <td className="px-3 py-3 text-center font-mono">
                  {ypa(totals.pass_yards, totals.pass_attempts)}
                </td>
              </>
            )}
            {(isQB || isRB) && (
              <>
                <td className="px-3 py-3 text-center font-mono">{totals.rush_attempts}</td>
                <td className="px-3 py-3 text-center font-mono">{fmt(totals.rush_yards)}</td>
                <td className="px-3 py-3 text-center font-mono">{totals.rush_tds}</td>
              </>
            )}
            {(isRB || isWR) && (
              <>
                <td className="px-3 py-3 text-center font-mono">{totals.targets}</td>
                <td className="px-3 py-3 text-center font-mono">{totals.receptions}</td>
                <td className="px-3 py-3 text-center font-mono">{fmt(totals.receiving_yards)}</td>
                <td className="px-3 py-3 text-center font-mono">{totals.receiving_tds}</td>
              </>
            )}
            <td className="px-3 py-3 text-center font-mono">{totals.fantasy_points.toFixed(1)}</td>
            <td className="px-3 py-3 text-center">—</td>
            <td className="px-3 py-3 text-center">—</td>
          </tr>
        </tfoot>
      </table>

      {/* Heatmap Legend */}
      <div className="bg-slate-100 px-4 py-3 border-t border-slate-300">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-600">
            Percentile among {position}s that season
          </span>
          <div className="flex items-center gap-0.5">
            <span className="px-2 py-1 text-xs font-medium rounded-l" style={{ backgroundColor: '#fca5a5' }}>0</span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#fecaca' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#fed7aa' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#ffedd5' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#fef9c3' }}>50</span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#dcfce7' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#bbf7d0' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#86efac' }}></span>
            <span className="px-2 py-1 text-xs" style={{ backgroundColor: '#4ade80' }}></span>
            <span className="px-2 py-1 text-xs font-medium rounded-r text-white" style={{ backgroundColor: '#22c55e' }}>100</span>
          </div>
        </div>
      </div>
    </div>
  );
}
