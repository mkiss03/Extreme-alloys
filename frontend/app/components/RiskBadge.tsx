/**
 * RiskBadge Component - Color-coded risk level indicator
 * Shows Low/Medium/High risk based on failure probability
 */

import React from 'react';

interface RiskBadgeProps {
  failureProbability: number; // 0 to 1
}

export default function RiskBadge({ failureProbability }: RiskBadgeProps) {
  // Determine risk level
  const getRiskLevel = (): 'low' | 'medium' | 'high' => {
    if (failureProbability < 0.3) return 'low';
    if (failureProbability < 0.6) return 'medium';
    return 'high';
  };

  const riskLevel = getRiskLevel();

  // Styling based on risk level
  const riskStyles = {
    low: {
      bg: 'bg-green-100',
      border: 'border-green-500',
      text: 'text-green-800',
      label: 'Low Risk'
    },
    medium: {
      bg: 'bg-yellow-100',
      border: 'border-yellow-500',
      text: 'text-yellow-800',
      label: 'Medium Risk'
    },
    high: {
      bg: 'bg-red-100',
      border: 'border-red-500',
      text: 'text-red-800',
      label: 'High Risk'
    }
  };

  const style = riskStyles[riskLevel];
  const percentage = (failureProbability * 100).toFixed(1);

  return (
    <div className={`${style.bg} ${style.border} border-l-4 px-4 py-3 rounded-r-lg shadow-sm`}>
      <div className="flex items-center justify-between">
        <div>
          <div className={`${style.text} font-bold text-sm`}>
            {style.label}
          </div>
          <div className={`${style.text} text-xs mt-0.5`}>
            Failure Probability: {percentage}%
          </div>
        </div>

        {/* Risk icon */}
        <div className={`${style.text}`}>
          {riskLevel === 'low' && (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
          {riskLevel === 'medium' && (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          )}
          {riskLevel === 'high' && (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>
      </div>
    </div>
  );
}
