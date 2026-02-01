/**
 * MethodologyPage - Explains how player similarity is calculated.
 *
 * Provides transparency about the algorithm and methodology
 * used to find similar NFL players.
 */

import { Link } from 'react-router-dom';

export function MethodologyPage() {
  return (
    <div className="max-w-3xl mx-auto">
      {/* Back link */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Search
      </Link>

      <h1 className="text-3xl font-bold text-slate-900 mb-8">How It Works</h1>

      {/* Overview */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Overview</h2>
        <p className="text-slate-600 leading-relaxed">
          This tool finds historically similar NFL players based on their statistical production.
          By comparing a player's stats against thousands of historical player-seasons, we can
          identify players who had similar career trajectories — useful for projecting future
          performance or finding comparable players for fantasy football analysis.
        </p>
      </section>

      {/* Algorithm */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">The Algorithm</h2>
        <div className="space-y-4 text-slate-600 leading-relaxed">
          <p>
            Player similarity is calculated using a weighted combination of three components:
          </p>

          <div className="bg-slate-50 rounded-lg p-5 space-y-4">
            <div>
              <h3 className="font-semibold text-slate-800">1. Statistical Distance (60% weight)</h3>
              <p className="text-sm mt-1">
                We calculate the Euclidean distance between players' normalized stats. Stats are
                z-score normalized within the dataset, then weighted by position relevance:
              </p>
              <ul className="text-sm mt-2 ml-4 list-disc space-y-1">
                <li><strong>QBs:</strong> Pass yards, pass TDs, interceptions, rushing yards</li>
                <li><strong>RBs:</strong> Rush yards, rush TDs, receptions, receiving yards</li>
                <li><strong>WRs/TEs:</strong> Targets, receptions, receiving yards, receiving TDs</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-slate-800">2. Fantasy Point Similarity (30% weight)</h3>
              <p className="text-sm mt-1">
                Compares total fantasy points scored over the comparison period. This captures
                overall offensive production in a single metric.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-slate-800">3. Draft Capital Similarity (10% weight)</h3>
              <p className="text-sm mt-1">
                Players drafted in similar positions tend to have similar expectations and
                opportunities. This component compares draft round and position pick.
              </p>
            </div>
          </div>

          <p>
            The final similarity score combines these three components. <strong>Lower scores
            indicate more similar players</strong> (0 = identical).
          </p>
        </div>
      </section>

      {/* Comparison Modes */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Comparison Modes</h2>
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
            <h3 className="font-semibold text-blue-900">Season Number Mode</h3>
            <p className="text-blue-800 text-sm mt-1">
              Compares players' 1st season to other players' 1st seasons, 2nd to 2nd, etc.
              This is the default mode and works well for comparing players at similar
              career stages regardless of when they entered the league.
            </p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-5">
            <h3 className="font-semibold text-purple-900">Age Mode</h3>
            <p className="text-purple-800 text-sm mt-1">
              Compares players at the same ages. Useful when comparing players who entered
              the NFL at different ages — for example, a 21-year-old rookie vs. a 24-year-old
              rookie who stayed in college longer.
            </p>
          </div>
        </div>
      </section>

      {/* Scoring Formats */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Scoring Formats</h2>
        <p className="text-slate-600 mb-4">
          Fantasy points are calculated based on your selected scoring format:
        </p>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <div className="font-bold text-slate-800">Standard</div>
            <div className="text-sm text-slate-500">0 PPR</div>
            <div className="text-xs text-slate-400 mt-1">No points per reception</div>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 text-center border-2 border-blue-300">
            <div className="font-bold text-slate-800">Half PPR</div>
            <div className="text-sm text-slate-500">0.5 PPR</div>
            <div className="text-xs text-slate-400 mt-1">+0.5 pts per reception</div>
          </div>
          <div className="bg-slate-50 rounded-lg p-4 text-center">
            <div className="font-bold text-slate-800">Full PPR</div>
            <div className="text-sm text-slate-500">1.0 PPR</div>
            <div className="text-xs text-slate-400 mt-1">+1.0 pts per reception</div>
          </div>
        </div>
      </section>

      {/* Data Source */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Data Source</h2>
        <p className="text-slate-600 leading-relaxed">
          All player data comes from{' '}
          <a
            href="https://github.com/nflverse"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            nflverse
          </a>
          , an open-source collection of NFL data including play-by-play data,
          player statistics, and roster information. The database includes players
          from 1999 to present.
        </p>
      </section>

      {/* Limitations */}
      <section className="mb-10">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Limitations</h2>
        <ul className="text-slate-600 space-y-2 list-disc ml-5">
          <li>
            <strong>Era differences:</strong> The NFL has evolved significantly over time.
            Comparing modern pass-heavy offenses to older run-heavy schemes has inherent limitations.
          </li>
          <li>
            <strong>Context matters:</strong> Stats don't capture everything — coaching systems,
            supporting cast, and injuries all affect production but aren't factored in.
          </li>
          <li>
            <strong>Sample size:</strong> Players with shorter careers have fewer data points,
            making comparisons less reliable.
          </li>
          <li>
            <strong>Qualified players only:</strong> Players must have minimum games played
            to be included in percentile calculations.
          </li>
        </ul>
      </section>

      {/* Back to search */}
      <div className="border-t border-slate-200 pt-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
        >
          Start Searching Players
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </div>
  );
}
