// frontend/app/api-client.ts
// Updated to use NEXT_PUBLIC_BACKEND_URL for backend base URL
/**
 * API client for communicating with the Extreme Alloys backend
 */

import axios, { AxiosInstance } from 'axios';

// Read backend URL from environment variable (falls back to localhost for development)
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Dev logging - show which backend URL is being used
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('[ExtremeAlloys] Using backend URL:', API_BASE_URL);
}

// Export API_BASE_URL for use in other components if needed
export { API_BASE_URL };

export interface AlloyPredictionRequest {
  composition: string;
  temperature_c: number;
  pressure_mpa: number;
  cycles: number;
  model_type?: string;
}

export interface AlloyPredictionResponse {
  creep_lifetime_hours: number;
  failure_probability: number;
  stress_limit_mpa: number;
  model_version: string;
  confidence: number;
}

export interface ReportResponse {
  input_parameters: AlloyPredictionRequest;
  predictions: AlloyPredictionResponse;
  recommendations: string[];
  metadata: {
    report_version: string;
    analysis_type: string;
  };
}

class AlloyAPIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get API health status
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/predict/health');
    return response.data;
  }

  /**
   * Predict alloy behavior under extreme conditions
   */
  async predictAlloyBehavior(
    request: AlloyPredictionRequest
  ): Promise<AlloyPredictionResponse> {
    const response = await this.client.post('/predict/extreme_alloy', request);
    return response.data;
  }

  /**
   * Generate comprehensive prediction report
   */
  async generateReport(
    request: AlloyPredictionRequest
  ): Promise<ReportResponse> {
    const response = await this.client.post('/predict/report', request);
    return response.data;
  }
}

export const apiClient = new AlloyAPIClient();
