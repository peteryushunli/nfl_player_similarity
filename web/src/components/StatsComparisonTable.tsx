/**
 * StatsComparisonTable - Clean tabular display of stats comparison.
 *
 * Shows stats as columns with players as rows, plus difference rows
 * showing absolute and percent differences.
 */

import type { AggregatedStats } from '../types';

interface StatsComparisonTableProps {
  targetStats: AggregatedStats;
  compStats: AggregatedStats;
  targetName: string;
  compName: string;
  position: string;
}

// Helper to format values
function formatValue(v: number, format: 'number' | 'decimal' = 'number'): string {
  if (format === 'decimal') return v.toFixed(1);
  return v.toLocaleString();
}

// Helper to format diff with sign
function formatDiff(diff: number, format: 'number' | 'decimal' = 'number'): string {
  if (diff === 0) return '—';
  const sign = diff > 0 ? '+' : '';
  return `${sign}${formatValue(diff, format)}`;
}

// Helper to format percent diff
function formatPctDiff(targetValue: number, compValue: number): string {
  if (targetValue === 0) {
    if (compValue === 0) return '—';
    return compValue > 0 ? '+∞%' : '-∞%';
  }
  const pctDiff = ((compValue - targetValue) / Math.abs(targetValue)) * 100;
  if (pctDiff === 0) return '—';
  const sign = pctDiff > 0 ? '+' : '';
  return `${sign}${pctDiff.toFixed(1)}%`;
}

// Helper to get diff color class
function getDiffColor(diff: number): string {
  if (diff > 0) return 'text-green-600';
  if (diff < 0) return 'text-red-600';
  return 'text-gray-400';
}

interface StatConfig {
  key: string;
  label: string;
  format: 'number' | 'decimal';
  getValue: (stats: AggregatedStats) => number;
}

export function StatsComparisonTable({
  targetStats,
  compStats,
  targetName,
  compName,
  position,
}: StatsComparisonTableProps) {
  const isQB = position === 'QB';
  const isRB = position === 'RB';
  const isWR = position === 'WR' || position === 'TE';

  // Build stat configs based on position
  const stats: StatConfig[] = [
    { key: 'games', label: 'G', format: 'number', getValue: (s) => s.games_played },
  ];

  if (isQB) {
    stats.push(
      { key: 'pass_yards', label: 'Pass Yds', format: 'number', getValue: (s) => s.pass_yards },
      { key: 'pass_tds', label: 'Pass TD', format: 'number', getValue: (s) => s.pass_tds },
      { key: 'pass_comp', label: 'Cmp', format: 'number', getValue: (s) => s.pass_completions },
      { key: 'pass_att', label: 'Att', format: 'number', getValue: (s) => s.pass_attempts },
      { key: 'ints', label: 'INT', format: 'number', getValue: (s) => s.interceptions },
    );
  }

  if (isQB || isRB) {
    stats.push(
      { key: 'rush_yards', label: 'Rush Yds', format: 'number', getValue: (s) => s.rush_yards },
      { key: 'rush_tds', label: 'Rush TD', format: 'number', getValue: (s) => s.rush_tds },
      { key: 'rush_att', label: 'Carries', format: 'number', getValue: (s) => s.rush_attempts },
    );
  }

  if (isRB || isWR) {
    stats.push(
      { key: 'rec_yards', label: 'Rec Yds', format: 'number', getValue: (s) => s.receiving_yards },
      { key: 'rec_tds', label: 'Rec TD', format: 'number', getValue: (s) => s.receiving_tds },
      { key: 'rec', label: 'Rec', format: 'number', getValue: (s) => s.receptions },
      { key: 'targets', label: 'Tgt', format: 'number', getValue: (s) => s.targets },
    );
  }

  stats.push(
    { key: 'fantasy', label: 'Fantasy', format: 'decimal', getValue: (s) => s.fantasy_points },
  );

  // Shorten names for display
  const shortTarget = targetName.split(' ').pop() || targetName;
  const shortComp = compName.split(' ').pop() || compName;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide sticky left-0 bg-white">
              Player
            </th>
            {stats.map((stat) => (
              <th
                key={stat.key}
                className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide text-right whitespace-nowrap"
              >
                {stat.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {/* Target player row */}
          <tr className="border-b border-gray-100 bg-blue-50">
            <td className="px-2 py-2 font-medium text-gray-900 sticky left-0 bg-blue-50 whitespace-nowrap">
              {shortTarget}
            </td>
            {stats.map((stat) => (
              <td key={stat.key} className="px-2 py-2 text-right font-medium text-gray-800 font-mono">
                {formatValue(stat.getValue(targetStats), stat.format)}
              </td>
            ))}
          </tr>

          {/* Comparison player row */}
          <tr className="border-b border-gray-100 hover:bg-gray-50">
            <td className="px-2 py-2 font-medium text-gray-900 sticky left-0 bg-white whitespace-nowrap">
              {shortComp}
            </td>
            {stats.map((stat) => (
              <td key={stat.key} className="px-2 py-2 text-right font-medium text-gray-800 font-mono">
                {formatValue(stat.getValue(compStats), stat.format)}
              </td>
            ))}
          </tr>

          {/* Absolute difference row */}
          <tr className="border-b border-gray-100 bg-gray-50">
            <td className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase sticky left-0 bg-gray-50">
              Diff
            </td>
            {stats.map((stat) => {
              const targetVal = stat.getValue(targetStats);
              const compVal = stat.getValue(compStats);
              const diff = compVal - targetVal;
              return (
                <td key={stat.key} className={`px-2 py-2 text-right font-mono text-xs ${getDiffColor(diff)}`}>
                  {formatDiff(diff, stat.format)}
                </td>
              );
            })}
          </tr>

          {/* Percent difference row */}
          <tr className="bg-gray-50">
            <td className="px-2 py-2 text-xs font-semibold text-gray-500 uppercase sticky left-0 bg-gray-50">
              Diff %
            </td>
            {stats.map((stat) => {
              const targetVal = stat.getValue(targetStats);
              const compVal = stat.getValue(compStats);
              const diff = compVal - targetVal;
              return (
                <td key={stat.key} className={`px-2 py-2 text-right font-mono text-xs ${getDiffColor(diff)}`}>
                  {formatPctDiff(targetVal, compVal)}
                </td>
              );
            })}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
