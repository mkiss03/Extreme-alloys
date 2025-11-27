// frontend/app/api-client.ts
/**
 * API client for communicating with the Extreme Alloys backend
 */

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

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
