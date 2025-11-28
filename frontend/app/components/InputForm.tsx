// frontend/app/components/InputForm.tsx
// UPDATED: Centralized API client, input validation, better error messages
'use client';

import React, { useState } from 'react';
import { predictAlloy, AlloyPredictionRequest, AlloyPredictionResponse } from '@/utils/apiClient';

interface InputFormProps {
  onPredictionComplete: (prediction: AlloyPredictionResponse) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

const InputForm: React.FC<InputFormProps> = ({
  onPredictionComplete,
  onError,
  onLoadingChange,
}) => {
  const [formData, setFormData] = useState<AlloyPredictionRequest>({
    composition: 'Ni:55,Cr:20,Mo:10,W:12,Co:3',
    temperature_c: 850,
    pressure_mpa: 150,
    cycles: 10000,
    model_type: 'gnn',
  });

  const [inputErrors, setInputErrors] = useState<Record<string, string>>({});

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    // Clear error for this field
    setInputErrors(prev => ({ ...prev, [name]: '' }));

    setFormData(prev => ({
      ...prev,
      [name]: name === 'composition' || name === 'model_type'
        ? value
        : name === 'cycles'
          ? parseInt(value) || 0
          : parseFloat(value) || 0,
    }));
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Validate composition
    if (!formData.composition || !formData.composition.includes(':')) {
      errors.composition = 'Composition must include Element:Percentage pairs';
    }

    // Validate temperature
    if (formData.temperature_c < 0) {
      errors.temperature_c = 'Temperature cannot be negative';
    }
    if (formData.temperature_c > 2000) {
      errors.temperature_c = 'Temperature exceeds realistic range (max 2000°C)';
    }

    // Validate pressure
    if (formData.pressure_mpa < 0) {
      errors.pressure_mpa = 'Pressure cannot be negative';
    }
    if (formData.pressure_mpa > 1000) {
      errors.pressure_mpa = 'Pressure exceeds typical range (max 1000 MPa)';
    }

    // Validate cycles
    if (formData.cycles < 0) {
      errors.cycles = 'Cycles cannot be negative';
    }

    setInputErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (!validateForm()) {
      onError('Please fix the input errors before submitting');
      return;
    }

    onLoadingChange(true);
    onError(''); // Clear previous errors

    try {
      const result = await predictAlloy(formData);
      onPredictionComplete(result);
    } catch (err: any) {
      console.error('Prediction error:', err);

      // User-friendly error message
      const errorMessage = err.message || 'Prediction request failed. Please try again.';
      onError(errorMessage);
    } finally {
      onLoadingChange(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Composition */}
      <div>
        <label htmlFor="composition" className="block text-sm font-semibold text-gray-700 mb-2">
          Alloy Composition
        </label>
        <input
          type="text"
          id="composition"
          name="composition"
          value={formData.composition}
          onChange={handleInputChange}
          className={`mt-1 block w-full rounded-lg border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 px-4 py-2.5 transition-all`}
          placeholder="Ni:55,Cr:20,Mo:10,W:12,Co:3"
        />
        {inputErrors.composition && (
          <p className="mt-1 text-sm text-red-600">{inputErrors.composition}</p>
        )}
        <p className="mt-1.5 text-xs text-gray-500">
          Format: Element:Percentage pairs separated by commas
        </p>
      </div>

      {/* Temperature */}
      <div>
        <label htmlFor="temperature_c" className="block text-sm font-semibold text-gray-700 mb-2">
          Temperature (°C)
        </label>
        <input
          type="number"
          id="temperature_c"
          name="temperature_c"
          value={formData.temperature_c}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-lg border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 px-4 py-2.5 transition-all"
          step="0.1"
          min="0"
          max="2000"
        />
        {inputErrors.temperature_c && (
          <p className="mt-1 text-sm text-red-600">{inputErrors.temperature_c}</p>
        )}
      </div>

      {/* Pressure */}
      <div>
        <label htmlFor="pressure_mpa" className="block text-sm font-semibold text-gray-700 mb-2">
          Pressure (MPa)
        </label>
        <input
          type="number"
          id="pressure_mpa"
          name="pressure_mpa"
          value={formData.pressure_mpa}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-lg border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 px-4 py-2.5 transition-all"
          step="0.1"
          min="0"
          max="1000"
        />
        {inputErrors.pressure_mpa && (
          <p className="mt-1 text-sm text-red-600">{inputErrors.pressure_mpa}</p>
        )}
      </div>

      {/* Cycles */}
      <div>
        <label htmlFor="cycles" className="block text-sm font-semibold text-gray-700 mb-2">
          Thermal/Mechanical Cycles
        </label>
        <input
          type="number"
          id="cycles"
          name="cycles"
          value={formData.cycles}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-lg border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 px-4 py-2.5 transition-all"
          step="1"
          min="0"
        />
        {inputErrors.cycles && (
          <p className="mt-1 text-sm text-red-600">{inputErrors.cycles}</p>
        )}
      </div>

      {/* Model Type */}
      <div>
        <label htmlFor="model_type" className="block text-sm font-semibold text-gray-700 mb-2">
          Prediction Model
        </label>
        <select
          id="model_type"
          name="model_type"
          value={formData.model_type}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 px-4 py-2.5 transition-all bg-white"
        >
          <option value="gnn">Graph Neural Network (Balanced)</option>
          <option value="physics_heuristic">Physics Heuristic (Theory-based)</option>
          <option value="safety_conservative">Safety Conservative (Most Cautious)</option>
        </select>
        <p className="mt-1.5 text-xs text-gray-500">
          Different models use different prediction strategies
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
      >
        Predict Behavior
      </button>
    </form>
  );
};

export default InputForm;
