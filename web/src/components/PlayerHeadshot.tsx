/**
 * PlayerHeadshot - Displays player headshot with fallback.
 *
 * Uses the headshot_url from API response.
 * Falls back to initials avatar if image fails to load or URL is null.
 */

import { useState } from 'react';

interface PlayerHeadshotProps {
  headshotUrl: string | null | undefined;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// Size configurations
const sizes = {
  sm: { container: 'w-8 h-8', text: 'text-xs' },
  md: { container: 'w-12 h-12', text: 'text-sm' },
  lg: { container: 'w-16 h-16', text: 'text-base' },
};

// Get initials from player name
function getInitials(name: string): string {
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
}

export function PlayerHeadshot({ headshotUrl, name, size = 'md', className = '' }: PlayerHeadshotProps) {
  const [hasError, setHasError] = useState(false);
  const sizeConfig = sizes[size];
  const initials = getInitials(name);

  // Show initials if no URL or image failed to load
  if (!headshotUrl || hasError) {
    return (
      <div
        className={`${sizeConfig.container} rounded-full bg-slate-200 flex items-center justify-center ${className}`}
      >
        <span className={`${sizeConfig.text} font-semibold text-slate-600`}>
          {initials}
        </span>
      </div>
    );
  }

  return (
    <img
      src={headshotUrl}
      alt={name}
      className={`${sizeConfig.container} rounded-full object-cover bg-slate-100 ${className}`}
      onError={() => setHasError(true)}
    />
  );
}
