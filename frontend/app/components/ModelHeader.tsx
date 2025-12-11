/**
 * ModelHeader Component - Display model metadata and information
 * Shows model type, strategy, version, and confidence
 */

import React from 'react';

interface ModelHeaderProps {
  modelType: string;
  modelStrategy: string;
  modelVersion: string;
  modelConfidence: number; // 0 to 1
}

export default function ModelHeader({
  modelType,
  modelStrategy,
  modelVersion,
  modelConfidence
}: ModelHeaderProps) {
  // Get strategy badge color
  const getStrategyColor = () => {
    switch (modelStrategy) {
      case 'data_driven_ml':
      case 'data_driven':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'physics_based':
      case 'physics_inspired':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'conservative_safety':
      case 'safety_conservative':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  // Format model type for display
  const formatModelType = (type: string): string => {
    const typeMap: Record<string, string> = {
      'gnn': 'GNN',
      'physics_heuristic': 'Physics Heuristic',
      'safety_conservative': 'Safety Conservative'
    };
    return typeMap[type] || type.toUpperCase();
  };

  // Format strategy for display
  const formatStrategy = (strategy: string): string => {
    return strategy
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const confidencePercentage = (modelConfidence * 100).toFixed(0);

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-5 border-2 border-gray-200 shadow-sm mb-6">
      {/* Top Row: Model Name and Strategy Badge */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {/* Model Icon */}
          <div className="bg-gray-700 text-white rounded-lg p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>

          {/* Model Name */}
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              {formatModelType(modelType)}
            </h3>
            <p className="text-xs text-gray-500">Prediction Model</p>
          </div>
        </div>

        {/* Strategy Badge */}
        <span className={`px-4 py-2 rounded-full text-sm font-semibold border-2 ${getStrategyColor()}`}>
          {formatStrategy(modelStrategy)}
        </span>
      </div>

      {/* Bottom Row: Version and Confidence */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-300">
        {/* Version */}
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <span className="text-sm text-gray-600">
            Version: <span className="font-mono font-semibold text-gray-800">{modelVersion}</span>
          </span>
        </div>

        {/* Confidence */}
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm text-gray-600">
            Confidence: <span className="font-bold text-gray-800">{confidencePercentage}%</span>
          </span>
        </div>
      </div>
    </div>
  );
}
