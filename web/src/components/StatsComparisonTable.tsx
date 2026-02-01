/**
 * StatsComparisonTable - Clean tabular display of stats comparison.
 *
 * Shows target player stats vs comparison player stats in a clean table format
 * with categories (Passing, Rushing, Receiving, Fantasy).
 */

import type { AggregatedStats } from '../types';

interface StatsComparisonTableProps {
  targetStats: AggregatedStats;
  compStats: AggregatedStats;
  targetName: string;
  compName: string;
  position: string;
}

// Category header row
function CategoryRow({ label }: { label: string }) {
  return (
    <tr className="bg-gray-50">
      <td colSpan={4} className="px-3 py-2 text-xs font-semibold text-gray-700 uppercase tracking-wide">
        {label}
      </td>
    </tr>
  );
}

// Stat row with optional diff highlighting
function StatRow({
  label,
  targetValue,
  compValue,
  format = 'number',
}: {
  label: string;
  targetValue: number;
  compValue: number;
  format?: 'number' | 'decimal';
}) {
  const diff = compValue - targetValue;
  const diffColor = diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-400';
  const diffSign = diff > 0 ? '+' : '';

  const formatValue = (v: number) => {
    if (format === 'decimal') return v.toFixed(1);
    return v.toLocaleString();
  };

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50">
      <td className="px-3 py-2 text-sm text-gray-600">{label}</td>
      <td className="px-3 py-2 text-sm text-gray-800 text-right font-medium">
        {formatValue(targetValue)}
      </td>
      <td className="px-3 py-2 text-sm text-gray-800 text-right font-medium">
        {formatValue(compValue)}
      </td>
      <td className={`px-3 py-2 text-sm text-right ${diffColor}`}>
        {diff !== 0 ? `${diffSign}${formatValue(diff)}` : '—'}
      </td>
    </tr>
  );
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

  // Shorten names for header if needed
  const shortTarget = targetName.split(' ').pop() || targetName;
  const shortComp = compName.split(' ').pop() || compName;

  return (
    <table className="w-full text-left">
      <thead>
        <tr className="border-b-2 border-gray-200">
          <th className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide w-1/3">
            Stat
          </th>
          <th className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide text-right w-1/5">
            {shortTarget}
          </th>
          <th className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide text-right w-1/5">
            {shortComp}
          </th>
          <th className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide text-right w-1/5">
            Diff
          </th>
        </tr>
      </thead>
      <tbody>
        {/* Games */}
        <CategoryRow label="Games" />
        <StatRow label="Games Played" targetValue={targetStats.games_played} compValue={compStats.games_played} />

        {/* Passing (QB) */}
        {isQB && (
          <>
            <CategoryRow label="Passing" />
            <StatRow label="Pass Yards" targetValue={targetStats.pass_yards} compValue={compStats.pass_yards} />
            <StatRow label="Pass TDs" targetValue={targetStats.pass_tds} compValue={compStats.pass_tds} />
            <StatRow label="Completions" targetValue={targetStats.pass_completions} compValue={compStats.pass_completions} />
            <StatRow label="Attempts" targetValue={targetStats.pass_attempts} compValue={compStats.pass_attempts} />
            <StatRow label="INTs" targetValue={targetStats.interceptions} compValue={compStats.interceptions} />
          </>
        )}

        {/* Rushing (QB, RB) */}
        {(isQB || isRB) && (
          <>
            <CategoryRow label="Rushing" />
            <StatRow label="Rush Yards" targetValue={targetStats.rush_yards} compValue={compStats.rush_yards} />
            <StatRow label="Rush TDs" targetValue={targetStats.rush_tds} compValue={compStats.rush_tds} />
            <StatRow label="Carries" targetValue={targetStats.rush_attempts} compValue={compStats.rush_attempts} />
          </>
        )}

        {/* Receiving (RB, WR, TE) */}
        {(isRB || isWR) && (
          <>
            <CategoryRow label="Receiving" />
            <StatRow label="Rec Yards" targetValue={targetStats.receiving_yards} compValue={compStats.receiving_yards} />
            <StatRow label="Rec TDs" targetValue={targetStats.receiving_tds} compValue={compStats.receiving_tds} />
            <StatRow label="Receptions" targetValue={targetStats.receptions} compValue={compStats.receptions} />
            <StatRow label="Targets" targetValue={targetStats.targets} compValue={compStats.targets} />
          </>
        )}

        {/* Fantasy */}
        <CategoryRow label="Fantasy" />
        <StatRow
          label="Half PPR Points"
          targetValue={targetStats.fantasy_points}
          compValue={compStats.fantasy_points}
          format="decimal"
        />
      </tbody>
    </table>
  );
}
