// frontend/app/page.tsx
// UPDATED: Import from utils/apiClient, improved layout spacing
'use client';

import { useState } from 'react';
import Layout from './components/Layout';
import InputForm from './components/InputForm';
import ResultsView from './components/ResultsView';
import { AlloyPredictionResponse } from '@/utils/apiClient';

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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Extreme Alloys Predictor
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered prediction for alloy behavior under extreme conditions using multiple model strategies
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Input Parameters</h2>
            <InputForm
              onPredictionComplete={handlePredictionComplete}
              onError={handleError}
              onLoadingChange={handleLoadingChange}
            />
          </div>

          {/* Results Display */}
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Prediction Results</h2>
            
            {isLoading && (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-4"></div>
                <div className="text-gray-600 text-lg">Running prediction...</div>
              </div>
            )}
            
            {error && !isLoading && (
              <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-r-lg shadow-sm">
                <div className="font-semibold mb-1">Prediction Error</div>
                <div className="text-sm">{error}</div>
              </div>
            )}
            
            {prediction && !isLoading && (
              <ResultsView prediction={prediction} />
            )}
            
            {!prediction && !isLoading && !error && (
              <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                <svg className="w-20 h-20 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p className="text-lg font-medium">Enter parameters and predict</p>
                <p className="text-sm mt-1">Results will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
