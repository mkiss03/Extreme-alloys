// frontend/app/components/InputForm.tsx
'use client';

import React, { useState } from 'react';
import { apiClient, AlloyPredictionRequest, AlloyPredictionResponse } from '../api-client';

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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'composition' || name === 'model_type'
        ? value
        : parseFloat(value),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    onLoadingChange(true);

    try {
      const result = await apiClient.predictAlloyBehavior(formData);
      onPredictionComplete(result);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to get prediction';
      onError(errorMessage);
    } finally {
      onLoadingChange(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="composition" className="block text-sm font-medium text-gray-700">
          Alloy Composition
        </label>
        <input
          type="text"
          id="composition"
          name="composition"
          value={formData.composition}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
          placeholder="Ni:55,Cr:20,Mo:10,W:12,Co:3"
        />
        <p className="mt-1 text-sm text-gray-500">
          Format: Element:Percentage pairs separated by commas
        </p>
      </div>

      <div>
        <label htmlFor="temperature_c" className="block text-sm font-medium text-gray-700">
          Temperature (°C)
        </label>
        <input
          type="number"
          id="temperature_c"
          name="temperature_c"
          value={formData.temperature_c}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
          step="0.1"
        />
      </div>

      <div>
        <label htmlFor="pressure_mpa" className="block text-sm font-medium text-gray-700">
          Pressure (MPa)
        </label>
        <input
          type="number"
          id="pressure_mpa"
          name="pressure_mpa"
          value={formData.pressure_mpa}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
          step="0.1"
        />
      </div>

      <div>
        <label htmlFor="cycles" className="block text-sm font-medium text-gray-700">
          Thermal/Mechanical Cycles
        </label>
        <input
          type="number"
          id="cycles"
          name="cycles"
          value={formData.cycles}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
          step="1"
        />
      </div>

      <div>
        <label htmlFor="model_type" className="block text-sm font-medium text-gray-700">
          Model Type
        </label>
        <select
          id="model_type"
          name="model_type"
          value={formData.model_type}
          onChange={handleInputChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 border"
        >
          <option value="gnn">Graph Neural Network</option>
          <option value="creep">Creep Model</option>
          <option value="ensemble">Ensemble</option>
        </select>
      </div>

      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
      >
        Predict Behavior
      </button>
    </form>
  );
};

export default InputForm;
