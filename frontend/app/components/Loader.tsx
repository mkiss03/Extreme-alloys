/**
 * Loader Component - Modern spinning loader
 * Used during prediction API calls
 */

import React from 'react';

interface LoaderProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

export default function Loader({ message = 'Loading...', size = 'large' }: LoaderProps) {
  // Size mapping
  const sizeClasses = {
    small: 'h-8 w-8 border-2',
    medium: 'h-12 w-12 border-3',
    large: 'h-16 w-16 border-4'
  };

  const textSizes = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  return (
    <div className="flex flex-col items-center justify-center h-96">
      {/* Spinning circle */}
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-blue-600 border-t-transparent mb-4`}
        role="status"
        aria-label="Loading"
      />

      {/* Loading message */}
      <div className={`text-gray-600 ${textSizes[size]} font-medium`}>
        {message}
      </div>

      {/* Optional pulsing dots */}
      <div className="flex space-x-1 mt-2">
        <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
        <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></div>
        <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  );
}
