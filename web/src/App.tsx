/**
 * App.tsx - Root component of the React application.
 *
 * This file sets up:
 * - React Router for navigation between pages
 * - TanStack Query provider for API data fetching
 * - The Layout wrapper around all pages
 *
 * Adding new pages:
 * 1. Create the page component in src/pages/
 * 2. Add a new Route element below
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { PlayerDetailPage } from './pages/PlayerDetailPage';
import { MethodologyPage } from './pages/MethodologyPage';

// Create a QueryClient instance for TanStack Query
// This manages caching and request deduplication
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Don't refetch on window focus by default
      refetchOnWindowFocus: false,
      // Retry failed requests once
      retry: 1,
    },
  },
});

function App() {
  return (
    // QueryClientProvider makes TanStack Query available to all components
    <QueryClientProvider client={queryClient}>
      {/* BrowserRouter enables client-side routing */}
      <BrowserRouter>
        {/* Layout wraps all pages with header/footer */}
        <Layout>
          {/* Routes define which component to show for each URL path */}
          <Routes>
            {/* Home page - main search and results */}
            <Route path="/" element={<HomePage />} />

            {/* Player detail page - :gsisId is a URL parameter */}
            <Route path="/player/:gsisId" element={<PlayerDetailPage />} />

            {/* Methodology page - explains how similarity works */}
            <Route path="/methodology" element={<MethodologyPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
