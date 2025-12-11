// frontend/app/components/ResultsView.tsx
// v2.0: Refactored with modular components (ModelHeader, MetricCard, RiskBadge)
'use client';

import React from 'react';
import { AlloyPredictionResponse } from '@/utils/apiClient';
import ModelHeader from './ModelHeader';
import MetricCard from './MetricCard';
import RiskBadge from './RiskBadge';

interface ResultsViewProps {
  prediction: AlloyPredictionResponse;
}

const ResultsView: React.FC<ResultsViewProps> = ({ prediction }) => {
  return (
    <div className="space-y-6">
      {/* Model Information Header */}
      <ModelHeader
        modelType={prediction.model_type}
        modelStrategy={prediction.model_strategy}
        modelVersion={prediction.model_version}
        modelConfidence={prediction.model_confidence}
      />

      {/* Risk Badge */}
      <RiskBadge failureProbability={prediction.failure_probability} />

      {/* Prediction Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Creep Lifetime"
          value={prediction.creep_lifetime_hours}
          unit="hours"
          type="lifetime"
          subtitle="Expected operational lifespan under creep conditions"
        />

        <MetricCard
          title="Failure Probability"
          value={prediction.failure_probability}
          unit="probability"
          type="probability"
          subtitle="Likelihood of material failure"
        />

        <MetricCard
          title="Stress Limit"
          value={prediction.stress_limit_mpa}
          unit="MPa"
          type="stress"
          subtitle="Maximum recommended operating stress"
        />
      </div>

      {/* Physics Metadata (if available) */}
      {prediction.physics_metadata && (
        <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-bold text-purple-900 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Physics Metadata
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(prediction.physics_metadata).map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg p-3 border border-purple-200">
                <div className="text-purple-600 font-semibold text-xs uppercase tracking-wide mb-1">
                  {key.replace(/_/g, ' ')}
                </div>
                <div className="text-purple-900 font-mono">
                  {typeof value === 'number' ? value.toFixed(3) : String(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safety Factors (if available) */}
      {prediction.safety_factors && (
        <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-bold text-orange-900 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Safety Factors Applied
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(prediction.safety_factors).map(([key, value]) => {
              // Skip non-numeric descriptive fields
              if (typeof value !== 'number') return null;

              return (
                <div key={key} className="bg-white rounded-lg p-3 border border-orange-200">
                  <div className="text-orange-600 font-semibold text-xs uppercase tracking-wide mb-1">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div className="text-orange-900 font-bold text-lg">
                    {value < 1 ? `${(value * 100).toFixed(0)}%` : `${value.toFixed(2)}x`}
                  </div>
                </div>
              );
            })}
          </div>
          {prediction.safety_factors.description && (
            <div className="mt-3 text-sm text-orange-700 italic bg-white rounded-lg p-3 border border-orange-200">
              {prediction.safety_factors.description}
            </div>
          )}
        </div>
      )}

      {/* ML Metadata (if available - for GNN model) */}
      {prediction.ml_metadata && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            ML Model Info
          </h3>
          <div className="text-sm text-blue-800 space-y-2">
            {Object.entries(prediction.ml_metadata).map(([key, value]) => (
              <div key={key} className="flex justify-between bg-white rounded-lg p-2 border border-blue-200">
                <span className="font-semibold">{key.replace(/_/g, ' ')}:</span>
                <span className="font-mono">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsView;
