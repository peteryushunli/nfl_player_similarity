/**
 * CareerTrajectoryChart - Line chart showing fantasy point trajectories.
 *
 * Features:
 * - Target player shown as thick line
 * - Similar players shown as thinner lines with distinct colors
 * - Solid lines for seasons within comparison range
 * - Dashed lines for seasons beyond comparison range (projections)
 * - Interactive tooltips
 */

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
}

// Color palette for similar players (distinct, visible colors)
const PLAYER_COLORS = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
];

const TARGET_COLOR = '#0f172a'; // slate-900

export function CareerTrajectoryChart({
  targetName,
  targetCareerData,
  similarPlayers,
  comparisonEndSeason,
}: CareerTrajectoryChartProps) {
  // Build unified data structure for the chart
  // Each player gets TWO data keys: one for solid (within range) and one for dashed (beyond range)
  const top5Players = similarPlayers.slice(0, 5);

  const maxSeasons = Math.max(
    targetCareerData.length,
    ...top5Players.map(p => p.career_data?.length || 0)
  );

  // Create data points for each season number
  const chartData: Record<string, number | string | null>[] = [];

  for (let seasonNum = 1; seasonNum <= maxSeasons; seasonNum++) {
    const isWithinComparison = seasonNum <= comparisonEndSeason;
    const dataPoint: Record<string, number | string | null> = {
      season_number: seasonNum,
    };

    // Add target player data (split into solid/dashed)
    const targetPoint = targetCareerData.find(d => d.season_number === seasonNum);
    if (targetPoint) {
      if (isWithinComparison) {
        dataPoint[`${targetName}_solid`] = targetPoint.fantasy_points;
        // Add overlap point for continuity
        if (seasonNum === comparisonEndSeason) {
          dataPoint[`${targetName}_dashed`] = targetPoint.fantasy_points;
        }
      } else {
        dataPoint[`${targetName}_dashed`] = targetPoint.fantasy_points;
      }
    }

    // Add similar players data (split into solid/dashed)
    top5Players.forEach((player) => {
      const playerPoint = player.career_data?.find(d => d.season_number === seasonNum);
      if (playerPoint) {
        if (isWithinComparison) {
          dataPoint[`${player.name}_solid`] = playerPoint.fantasy_points;
          // Add overlap point for continuity
          if (seasonNum === comparisonEndSeason) {
            dataPoint[`${player.name}_dashed`] = playerPoint.fantasy_points;
          }
        } else {
          dataPoint[`${player.name}_dashed`] = playerPoint.fantasy_points;
        }
      }
    });

    chartData.push(dataPoint);
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ dataKey: string; value: number; color: string }>; label?: number }) => {
    if (!active || !payload) return null;

    // Combine solid and dashed entries for same player
    const playerValues: Record<string, { value: number; color: string }> = {};
    payload.forEach(p => {
      if (p.value === null || p.value === undefined) return;
      const playerName = p.dataKey.replace(/_solid$/, '').replace(/_dashed$/, '');
      if (!playerValues[playerName] || p.value > playerValues[playerName].value) {
        playerValues[playerName] = { value: p.value, color: p.color };
      }
    });

    const entries = Object.entries(playerValues).sort((a, b) => b[1].value - a[1].value);

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
            {data.value?.toFixed(1)} pts
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
      <div className="flex items-center gap-3 mb-4">
        <div className="w-1.5 h-8 bg-blue-500 rounded-full" />
        <div>
          <h3 className="text-xl font-bold text-slate-800">Career Trajectory</h3>
          <p className="text-sm text-slate-500">
            Half-PPR fantasy points by season
          </p>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
              label={{ value: 'Fantasy Points', angle: -90, position: 'insideLeft', fill: '#64748b' }}
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
