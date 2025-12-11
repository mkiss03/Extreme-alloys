/**
 * MetricCard Component - Display prediction metrics with color coding
 * Shows creep lifetime, failure probability, and stress limit
 */

import React from 'react';

interface MetricCardProps {
  title: string;
  value: number;
  unit: string;
  type: 'lifetime' | 'stress' | 'probability';
  subtitle?: string;
}

export default function MetricCard({ title, value, unit, type, subtitle }: MetricCardProps) {
  // Color schemes based on metric type
  const getColorScheme = () => {
    switch (type) {
      case 'lifetime':
        return {
          bg: 'bg-gradient-to-br from-blue-50 to-blue-100',
          border: 'border-blue-300',
          icon: 'text-blue-600',
          value: 'text-blue-900'
        };
      case 'probability':
        return {
          bg: 'bg-gradient-to-br from-red-50 to-red-100',
          border: 'border-red-300',
          icon: 'text-red-600',
          value: 'text-red-900'
        };
      case 'stress':
        // Color based on stress value
        if (value > 300) {
          return {
            bg: 'bg-gradient-to-br from-green-50 to-green-100',
            border: 'border-green-300',
            icon: 'text-green-600',
            value: 'text-green-900'
          };
        } else if (value > 150) {
          return {
            bg: 'bg-gradient-to-br from-yellow-50 to-yellow-100',
            border: 'border-yellow-300',
            icon: 'text-yellow-600',
            value: 'text-yellow-900'
          };
        } else {
          return {
            bg: 'bg-gradient-to-br from-red-50 to-red-100',
            border: 'border-red-300',
            icon: 'text-red-600',
            value: 'text-red-900'
          };
        }
    }
  };

  const colors = getColorScheme();

  // Format value based on type
  const formatValue = () => {
    if (type === 'probability') {
      return (value * 100).toFixed(1);
    } else if (type === 'lifetime') {
      return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
    } else {
      return value.toFixed(1);
    }
  };

  // Get icon based on type
  const getIcon = () => {
    switch (type) {
      case 'lifetime':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'probability':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case 'stress':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
    }
  };

  return (
    <div className={`${colors.bg} ${colors.border} border-2 rounded-xl p-6 shadow-md transition-all hover:shadow-lg`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          {title}
        </h3>
        <div className={colors.icon}>
          {getIcon()}
        </div>
      </div>

      {/* Value */}
      <div className="mb-2">
        <div className={`${colors.value} text-4xl font-bold`}>
          {formatValue()}
        </div>
        <div className="text-gray-600 text-sm font-medium mt-1">
          {unit}
        </div>
      </div>

      {/* Subtitle/Additional Info */}
      {subtitle && (
        <div className="text-gray-500 text-xs mt-3 pt-3 border-t border-gray-300">
          {subtitle}
        </div>
      )}
    </div>
  );
}
