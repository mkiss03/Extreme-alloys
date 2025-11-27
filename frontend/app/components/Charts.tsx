// frontend/app/components/Charts.tsx
'use client';

import React from 'react';
import { AlloyPredictionResponse } from '../api-client';

interface ChartsProps {
  prediction: AlloyPredictionResponse;
}

const Charts: React.FC<ChartsProps> = ({ prediction }) => {
  // Simple progress bar visualization for now
  // In the future, this can use recharts for more complex visualizations

  const confidencePercent = prediction.confidence * 100;
  const failureProbPercent = prediction.failure_probability * 100;

  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Model Confidence</span>
          <span className="font-medium">{confidencePercent.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      <div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Failure Risk</span>
          <span className="font-medium">{failureProbPercent.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              failureProbPercent < 30
                ? 'bg-green-500'
                : failureProbPercent < 70
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${failureProbPercent}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default Charts;
