/**
 * PlayerDetailPage - placeholder for future player detail view.
 *
 * This page will show:
 * - Detailed player information
 * - Season-by-season stats
 * - Charts/visualizations
 * - Option to find similar players from this view
 *
 * For now, it's a placeholder that shows the concept.
 */

import { useParams, Link } from 'react-router-dom';

export function PlayerDetailPage() {
  // Get the player ID from the URL
  // e.g., /player/00-0033873 -> gsisId = '00-0033873'
  const { gsisId } = useParams<{ gsisId: string }>();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          Player Detail Page
        </h1>
        <p className="text-gray-500 mb-4">
          Player ID: {gsisId}
        </p>
        <p className="text-gray-400 text-sm mb-6">
          This page will show detailed stats, charts, and more.
          <br />
          Coming soon!
        </p>
        <Link
          to="/"
          className="inline-block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          ← Back to Search
        </Link>
      </div>
    </div>
  );
}
