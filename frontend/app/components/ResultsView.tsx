// frontend/app/components/ResultsView.tsx
// UPDATED: Display model metadata, improved design
'use client';

import React from 'react';
import { AlloyPredictionResponse } from '@/utils/apiClient';

interface ResultsViewProps {
  prediction: AlloyPredictionResponse;
}

const ResultsView: React.FC<ResultsViewProps> = ({ prediction }) => {
  const getRiskLevel = (prob: number) => {
    if (prob < 0.3) return 'Low Risk';
    if (prob < 0.7) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-50 rounded-lg p-4 border">
        <div className="flex justify-between mb-2">
          <h3 className="text-sm font-semibold">Model: {prediction.model_type}</h3>
          <span className="px-2 py-1 rounded text-xs bg-blue-100">{prediction.model_strategy}</span>
        </div>
        <div className="text-xs text-gray-600">Version: {prediction.model_version} | Confidence: {(prediction.model_confidence * 100).toFixed(0)}%</div>
      </div>

      <div className="space-y-4">
        <div className="bg-blue-50 rounded-xl p-5 border">
          <div className="text-sm text-blue-700 font-semibold">Creep Lifetime</div>
          <div className="text-4xl font-bold text-blue-900">{prediction.creep_lifetime_hours.toFixed(0)} hrs</div>
        </div>

        <div className="bg-red-50 rounded-xl p-5 border">
          <div className="text-sm text-red-700 font-semibold">Failure Probability</div>
          <div className="text-4xl font-bold text-red-900">{(prediction.failure_probability * 100).toFixed(1)}%</div>
          <div className="text-xs mt-2">{getRiskLevel(prediction.failure_probability)}</div>
        </div>

        <div className="bg-purple-50 rounded-xl p-5 border">
          <div className="text-sm text-purple-700 font-semibold">Stress Limit</div>
          <div className="text-4xl font-bold text-purple-900">{prediction.stress_limit_mpa.toFixed(1)} MPa</div>
        </div>
      </div>
    </div>
  );
};

export default ResultsView;
