// frontend/app/components/ResultsView.tsx
'use client';

import React from 'react';
import { AlloyPredictionResponse } from '../api-client';
import Charts from './Charts';

interface ResultsViewProps {
  prediction: AlloyPredictionResponse;
}

const ResultsView: React.FC<ResultsViewProps> = ({ prediction }) => {
  const getRiskLevel = (probability: number): { color: string; label: string } => {
    if (probability < 0.3) return { color: 'green', label: 'Low Risk' };
    if (probability < 0.7) return { color: 'yellow', label: 'Medium Risk' };
    return { color: 'red', label: 'High Risk' };
  };

  const risk = getRiskLevel(prediction.failure_probability);

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm text-blue-600 font-medium">Creep Lifetime</div>
          <div className="text-3xl font-bold text-blue-900">
            {prediction.creep_lifetime_hours.toFixed(1)} hrs
          </div>
        </div>

        <div className={`bg-${risk.color}-50 rounded-lg p-4`}>
          <div className={`text-sm text-${risk.color}-600 font-medium`}>
            Failure Probability
          </div>
          <div className={`text-3xl font-bold text-${risk.color}-900`}>
            {(prediction.failure_probability * 100).toFixed(1)}%
          </div>
          <div className={`text-sm text-${risk.color}-600 mt-1`}>
            {risk.label}
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-sm text-purple-600 font-medium">Stress Limit</div>
          <div className="text-3xl font-bold text-purple-900">
            {prediction.stress_limit_mpa.toFixed(1)} MPa
          </div>
        </div>
      </div>

      {/* Charts */}
      <Charts prediction={prediction} />

      {/* Model Info */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm">
        <div className="flex justify-between mb-2">
          <span className="text-gray-600">Model Version:</span>
          <span className="font-medium">{prediction.model_version}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Confidence:</span>
          <span className="font-medium">
            {(prediction.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default ResultsView;
