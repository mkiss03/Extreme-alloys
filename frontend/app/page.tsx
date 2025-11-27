// frontend/app/page.tsx
'use client';

import { useState } from 'react';
import Layout from './components/Layout';
import InputForm from './components/InputForm';
import ResultsView from './components/ResultsView';
import { AlloyPredictionRequest, AlloyPredictionResponse } from './api-client';

export default function Home() {
  const [prediction, setPrediction] = useState<AlloyPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredictionComplete = (result: AlloyPredictionResponse) => {
    setPrediction(result);
    setError(null);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setPrediction(null);
  };

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Extreme Alloys Predictor
          </h1>
          <p className="text-xl text-gray-600">
            AI-powered prediction for alloy behavior under extreme conditions
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">Input Parameters</h2>
            <InputForm
              onPredictionComplete={handlePredictionComplete}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </div>

          {/* Results Display */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">Prediction Results</h2>
            {isLoading && (
              <div className="flex items-center justify-center h-64">
                <div className="text-gray-500">Loading predictions...</div>
              </div>
            )}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            {prediction && !isLoading && (
              <ResultsView prediction={prediction} />
            )}
            {!prediction && !isLoading && !error && (
              <div className="flex items-center justify-center h-64 text-gray-400">
                Enter parameters and click predict to see results
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
