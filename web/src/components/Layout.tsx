/**
 * Layout component - provides the basic page structure.
 *
 * Features a dark gradient header for a sports-media aesthetic.
 */

import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      {/* Header - Dark gradient for sports media aesthetic */}
      <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white shadow-xl">
        <div className="container mx-auto px-4 py-5">
          <div className="flex items-center gap-4">
            {/* Logo/Icon */}
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg
                className="w-7 h-7 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight">
                Player Similarity
              </h1>
              <p className="text-slate-400 text-sm">
                Find players with similar career trajectories
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content area */}
      <main className="container mx-auto px-4 py-8 flex-grow max-w-6xl">
        {children}
      </main>

      {/* Footer - Dark to match header */}
      <footer className="bg-slate-900 border-t border-slate-700 mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-slate-400 text-sm">
          Data from nflverse • Built with FastAPI + React
        </div>
      </footer>
    </div>
  );
}
