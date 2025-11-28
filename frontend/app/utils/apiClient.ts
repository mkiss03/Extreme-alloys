// frontend/lib/apiClient.ts
// NEW FILE: Centralized API client for all backend communication
/**
 * Centralized API client for Extreme Alloys backend
 * 
 * All API calls should go through this module to ensure:
 * - Consistent error handling
 * - Single source of truth for backend URL
 * - Type safety across the application
 */

// Read backend URL from environment (no fallback, fail fast if not set)
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!API_BASE_URL) {
  throw new Error(
    'NEXT_PUBLIC_BACKEND_URL is not set. ' +
    'Please configure this environment variable.'
  );
}

// Remove trailing slash to prevent double slashes
const baseURL = API_BASE_URL.replace(/\/$/, '');

// Log backend URL in development mode
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('[ExtremeAlloys API Client] Backend URL:', baseURL);
}

/**
 * Type definitions
 */
export interface AlloyPredictionRequest {
  composition: string;
  temperature_c: number;
  pressure_mpa: number;
  cycles: number;
  model_type?: 'gnn' | 'physics_heuristic' | 'safety_conservative';
}

export interface AlloyPredictionResponse {
  creep_lifetime_hours: number;
  failure_probability: number;
  stress_limit_mpa: number;
  model_type: string;
  model_strategy: string;
  model_version: string;
  model_confidence: number;
  physics_metadata?: Record<string, any>;
  safety_factors?: Record<string, number>;
}

export interface APIError {
  detail: string;
  status?: number;
}

/**
 * Main prediction function
 * 
 * @param request - Prediction request parameters
 * @returns Promise with prediction results
 * @throws Error with user-friendly message
 */
export async function predictAlloy(
  request: AlloyPredictionRequest
): Promise<AlloyPredictionResponse> {
  const url = `${baseURL}/api/v1/predict/extreme_alloy`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail = errorData.detail || `Server responded with status ${response.status}`;
      
      throw new Error(detail);
    }

    const data: AlloyPredictionResponse = await response.json();
    return data;

  } catch (error: any) {
    // Network error (no response from server)
    if (error.message === 'Failed to fetch') {
      throw new Error(
        'Unable to connect to the prediction service. ' +
        'Please check your internet connection or try again later.'
      );
    }

    // Re-throw with original message (already formatted)
    throw error;
  }
}

/**
 * Health check
 * 
 * @returns Promise with health status
 */
export async function checkHealth(): Promise<{ status: string }> {
  const url = `${baseURL}/health`;

  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Health check failed:', error);
    throw error;
  }
}

/**
 * Get available models
 * 
 * @returns Promise with list of available models
 */
export async function getAvailableModels(): Promise<any> {
  const url = `${baseURL}/api/v1/predict/models`;

  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Failed to get models:', error);
    throw error;
  }
}

// Export base URL for reference
export { baseURL as API_BASE_URL };
