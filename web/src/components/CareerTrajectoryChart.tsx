/**
 * CareerTrajectoryChart - Line chart showing fantasy point trajectories.
 *
 * Features:
 * - Tabbed interface: Fantasy Points vs Position Rank
 * - Target player shown as thick line
 * - Similar players shown as thinner lines with distinct colors
 * - Solid lines for seasons within comparison range
 * - Dashed lines for seasons beyond comparison range (projections)
 * - Interactive tooltips
 * - Position Rank view has inverted Y-axis (rank 1 at top)
 */

import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { CareerDataPoint, SimilarPlayer } from '../types';

interface CareerTrajectoryChartProps {
  targetName: string;
  targetCareerData: CareerDataPoint[];
  similarPlayers: SimilarPlayer[];
  comparisonEndSeason: number;  // Season number where comparison ends
  position: string;  // Player position for determining Y-axis range
}

type ChartView = 'fantasy_points' | 'position_rank';

// Color palette for similar players (distinct, visible colors)
const PLAYER_COLORS = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
];

const TARGET_COLOR = '#0f172a'; // slate-900

// Get a reasonable Y-axis max for position rank based on position
function getPositionRankMax(position: string): number {
  switch (position) {
    case 'QB': return 32;  // ~32 starting QBs
    case 'RB': return 48;  // More RBs rostered
    case 'WR': return 60;  // Most WRs rostered
    case 'TE': return 32;  // Fewer TEs
    default: return 48;
  }
}

// Get Y-axis ticks for position rank (always include 1 at top)
function getPositionRankTicks(position: string): number[] {
  switch (position) {
    case 'QB': return [1, 8, 16, 24, 32];
    case 'RB': return [1, 12, 24, 36, 48];
    case 'WR': return [1, 15, 30, 45, 60];
    case 'TE': return [1, 8, 16, 24, 32];
    default: return [1, 12, 24, 36, 48];
  }
}

export function CareerTrajectoryChart({
  targetName,
  targetCareerData,
  similarPlayers,
  comparisonEndSeason,
  position,
}: CareerTrajectoryChartProps) {
  const [activeView, setActiveView] = useState<ChartView>('fantasy_points');

  // Build unified data structure for the chart
  // Each player gets TWO data keys: one for solid (within range) and one for dashed (beyond range)
  const top5Players = similarPlayers.slice(0, 5);

  const maxSeasons = Math.max(
    targetCareerData.length,
    ...top5Players.map(p => p.career_data?.length || 0)
  );

  // Create data points for each season number (for fantasy points view)
  const fantasyChartData: Record<string, number | string | null>[] = [];
  // Create data points for position rank view
  const rankChartData: Record<string, number | string | null>[] = [];

  for (let seasonNum = 1; seasonNum <= maxSeasons; seasonNum++) {
    const isWithinComparison = seasonNum <= comparisonEndSeason;
    const fantasyDataPoint: Record<string, number | string | null> = {
      season_number: seasonNum,
    };
    const rankDataPoint: Record<string, number | string | null> = {
      season_number: seasonNum,
    };

    // Add target player data (split into solid/dashed)
    const targetPoint = targetCareerData.find(d => d.season_number === seasonNum);
    if (targetPoint) {
      if (isWithinComparison) {
        fantasyDataPoint[`${targetName}_solid`] = targetPoint.fantasy_points;
        if (targetPoint.fantasy_position_rank != null) {
          rankDataPoint[`${targetName}_solid`] = targetPoint.fantasy_position_rank;
        }
        // Add overlap point for continuity
        if (seasonNum === comparisonEndSeason) {
          fantasyDataPoint[`${targetName}_dashed`] = targetPoint.fantasy_points;
          if (targetPoint.fantasy_position_rank != null) {
            rankDataPoint[`${targetName}_dashed`] = targetPoint.fantasy_position_rank;
          }
        }
      } else {
        fantasyDataPoint[`${targetName}_dashed`] = targetPoint.fantasy_points;
        if (targetPoint.fantasy_position_rank != null) {
          rankDataPoint[`${targetName}_dashed`] = targetPoint.fantasy_position_rank;
        }
      }
    }

    // Add similar players data (split into solid/dashed)
    top5Players.forEach((player) => {
      const playerPoint = player.career_data?.find(d => d.season_number === seasonNum);
      if (playerPoint) {
        if (isWithinComparison) {
          fantasyDataPoint[`${player.name}_solid`] = playerPoint.fantasy_points;
          if (playerPoint.fantasy_position_rank != null) {
            rankDataPoint[`${player.name}_solid`] = playerPoint.fantasy_position_rank;
          }
          // Add overlap point for continuity
          if (seasonNum === comparisonEndSeason) {
            fantasyDataPoint[`${player.name}_dashed`] = playerPoint.fantasy_points;
            if (playerPoint.fantasy_position_rank != null) {
              rankDataPoint[`${player.name}_dashed`] = playerPoint.fantasy_position_rank;
            }
          }
        } else {
          fantasyDataPoint[`${player.name}_dashed`] = playerPoint.fantasy_points;
          if (playerPoint.fantasy_position_rank != null) {
            rankDataPoint[`${player.name}_dashed`] = playerPoint.fantasy_position_rank;
          }
        }
      }
    });

    fantasyChartData.push(fantasyDataPoint);
    rankChartData.push(rankDataPoint);
  }

  const chartData = activeView === 'fantasy_points' ? fantasyChartData : rankChartData;
  const yAxisLabel = activeView === 'fantasy_points' ? 'Fantasy Points' : 'Position Rank';
  const tooltipUnit = activeView === 'fantasy_points' ? 'pts' : '';

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ dataKey: string; value: number; color: string }>; label?: number }) => {
    if (!active || !payload) return null;

    // Combine solid and dashed entries for same player
    const playerValues: Record<string, { value: number; color: string }> = {};
    payload.forEach(p => {
      if (p.value === null || p.value === undefined) return;
      const playerName = p.dataKey.replace(/_solid$/, '').replace(/_dashed$/, '');
      // For fantasy points, higher is better; for rank, lower is better
      const shouldReplace = activeView === 'fantasy_points'
        ? (!playerValues[playerName] || p.value > playerValues[playerName].value)
        : (!playerValues[playerName] || p.value < playerValues[playerName].value);
      if (shouldReplace) {
        playerValues[playerName] = { value: p.value, color: p.color };
      }
    });

    // Sort: for fantasy points, higher first; for rank, lower first
    const entries = Object.entries(playerValues).sort((a, b) =>
      activeView === 'fantasy_points'
        ? b[1].value - a[1].value
        : a[1].value - b[1].value
    );

    return (
      <div className="bg-white border border-slate-200 shadow-lg rounded-lg p-3">
        <p className="font-bold text-slate-900 mb-2">
          Season {label}
          {label && label > comparisonEndSeason && (
            <span className="ml-2 text-xs font-normal text-slate-500">(projection)</span>
          )}
        </p>
        {entries.map(([name, data], idx) => (
          <p key={idx} className="text-sm" style={{ color: data.color }}>
            <span className="font-medium">{name}:</span>{' '}
            {activeView === 'fantasy_points'
              ? `${data.value?.toFixed(1)} ${tooltipUnit}`
              : `#${data.value}`
            }
          </p>
        ))}
      </div>
    );
  };

  // Custom legend that doesn't show duplicate entries
  const renderLegend = () => {
    const items = [
      { name: targetName, color: TARGET_COLOR },
      ...top5Players.map((p, i) => ({ name: p.name, color: PLAYER_COLORS[i] }))
    ];

    return (
      <div className="flex flex-wrap justify-center gap-4 mt-2">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div
              className="w-4 h-0.5"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-slate-700">{item.name}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-8 bg-blue-500 rounded-full" />
          <div>
            <h3 className="text-xl font-bold text-slate-800">Career Trajectory</h3>
            <p className="text-sm text-slate-500">
              {activeView === 'fantasy_points'
                ? 'Half-PPR fantasy points by season'
                : `${position} position rank by season`
              }
            </p>
          </div>
        </div>

        {/* Tab toggle */}
        <div className="inline-flex bg-slate-100 rounded-lg p-1">
          <button
            onClick={() => setActiveView('fantasy_points')}
            className={`px-4 py-2 rounded-md text-sm font-semibold transition-all ${
              activeView === 'fantasy_points'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Fantasy Points
          </button>
          <button
            onClick={() => setActiveView('position_rank')}
            className={`px-4 py-2 rounded-md text-sm font-semibold transition-all ${
              activeView === 'position_rank'
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Position Rank
          </button>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis
              dataKey="season_number"
              tick={{ fill: '#64748b', fontSize: 12 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={{ stroke: '#cbd5e1' }}
              label={{ value: 'Season', position: 'insideBottom', offset: -5, fill: '#64748b' }}
            />
            <YAxis
              tick={{ fill: '#64748b', fontSize: 12 }}
              axisLine={{ stroke: '#cbd5e1' }}
              tickLine={{ stroke: '#cbd5e1' }}
              label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', fill: '#64748b' }}
              reversed={activeView === 'position_rank'}
              domain={activeView === 'position_rank' ? [1, getPositionRankMax(position)] : ['auto', 'auto']}
              ticks={activeView === 'position_rank' ? getPositionRankTicks(position) : undefined}
              allowDataOverflow={activeView === 'position_rank'}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Reference line at comparison end */}
            <ReferenceLine
              x={comparisonEndSeason}
              stroke="#94a3b8"
              strokeDasharray="5 5"
              label={{
                value: 'Comparison ends',
                position: 'top',
                fill: '#64748b',
                fontSize: 10,
              }}
            />

            {/* Target player - solid portion */}
            <Line
              type="monotone"
              dataKey={`${targetName}_solid`}
              stroke={TARGET_COLOR}
              strokeWidth={3}
              dot={{ fill: TARGET_COLOR, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: TARGET_COLOR }}
              connectNulls
              legendType="none"
            />

            {/* Target player - dashed portion */}
            <Line
              type="monotone"
              dataKey={`${targetName}_dashed`}
              stroke={TARGET_COLOR}
              strokeWidth={3}
              strokeDasharray="8 4"
              dot={{ fill: TARGET_COLOR, strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: TARGET_COLOR }}
              connectNulls
              legendType="none"
            />

            {/* Similar players - solid portions */}
            {top5Players.map((player, idx) => (
              <Line
                key={`${player.gsis_id}_solid`}
                type="monotone"
                dataKey={`${player.name}_solid`}
                stroke={PLAYER_COLORS[idx]}
                strokeWidth={2}
                dot={{ fill: PLAYER_COLORS[idx], strokeWidth: 1, r: 3 }}
                activeDot={{ r: 5, fill: PLAYER_COLORS[idx] }}
                connectNulls
                legendType="none"
              />
            ))}

            {/* Similar players - dashed portions */}
            {top5Players.map((player, idx) => (
              <Line
                key={`${player.gsis_id}_dashed`}
                type="monotone"
                dataKey={`${player.name}_dashed`}
                stroke={PLAYER_COLORS[idx]}
                strokeWidth={2}
                strokeDasharray="8 4"
                dot={{ fill: PLAYER_COLORS[idx], strokeWidth: 1, r: 3 }}
                activeDot={{ r: 5, fill: PLAYER_COLORS[idx] }}
                connectNulls
                legendType="none"
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Custom legend */}
      {renderLegend()}

      {/* Legend explaining solid vs dashed */}
      <div className="mt-3 flex items-center justify-center gap-6 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <div className="w-6 h-0.5 bg-slate-600" />
          <span>Compared (Season 1–{comparisonEndSeason})</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 border-t-2 border-dashed border-slate-600" />
          <span>Beyond comparison</span>
        </div>
      </div>
    </div>
  );
}
