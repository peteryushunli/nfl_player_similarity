/**
 * Layout component - provides the basic page structure.
 *
 * This wraps all pages with a consistent header and container.
 * As the app grows, you can add navigation, footer, etc. here.
 */

import type { ReactNode } from 'react';

// Props interface defines what this component accepts
interface LayoutProps {
  children: ReactNode; // ReactNode means any valid React content
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-primary-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">NFL Player Similarity</h1>
          <p className="text-primary-200 text-sm">
            Find players with similar career trajectories
          </p>
        </div>
      </header>

      {/* Main content area */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer - you can add this later */}
      <footer className="bg-gray-100 border-t mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-gray-500 text-sm">
          Data from nflverse • Built with FastAPI + React
        </div>
      </footer>
    </div>
  );
}
