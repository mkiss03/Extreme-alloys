// frontend/app/utils/apiClient.ts
// v2.0: Enhanced API client with detailed error handling and timeout support
/**
 * Centralized API client for Extreme Alloys backend
 *
 * Features:
 * - Consistent error handling with detailed error types
 * - Request timeout management (10s default)
 * - Single source of truth for backend URL
 * - Type safety across the application
 * - Network/Backend/Validation error differentiation
 */

// Read backend URL from environment (no fallback, fail fast if not set)
const rawBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!rawBackendUrl) {
  throw new Error(
    'CRITICAL: NEXT_PUBLIC_BACKEND_URL is not set. ' +
    'Please configure this environment variable in your .env.local file. ' +
    'Example: NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com'
  );
}

// Remove trailing slash to prevent double slashes
const baseURL = rawBackendUrl.replace(/\/$/, '');

// Log backend URL in development mode
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('[API Client] Backend URL:', baseURL);
  console.log('[API Client] Environment:', process.env.NODE_ENV);
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
  safety_factors?: Record<string, any>;
  ml_metadata?: Record<string, any>;
}

export interface APIError {
  detail: string;
  status?: number;
  type: 'network' | 'validation' | 'server' | 'timeout';
}

export interface ModelInfo {
  name: string;
  confidence: number;
  strategy: string;
  description: string;
}

export interface ModelsResponse {
  total_models: number;
  models: ModelInfo[];
  default_model: string;
}

/**
 * Configuration
 */
const DEFAULT_TIMEOUT = 10000; // 10 seconds

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = DEFAULT_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('timeout');
    }
    throw error;
  }
}

/**
 * Main prediction function
 *
 * @param request - Prediction request parameters
 * @param timeout - Request timeout in milliseconds (default: 10000)
 * @returns Promise with prediction results
 * @throws Error with user-friendly message and error type
 */
export async function predictAlloy(
  request: AlloyPredictionRequest,
  timeout: number = DEFAULT_TIMEOUT
): Promise<AlloyPredictionResponse> {
  const url = `${baseURL}/api/v1/predict/extreme_alloy`;

  // Validate model type
  const validModels = ['gnn', 'physics_heuristic', 'safety_conservative'];
  if (request.model_type && !validModels.includes(request.model_type)) {
    console.warn(
      `[API Client] Warning: model_type '${request.model_type}' is not supported. ` +
      `Valid models: ${validModels.join(', ')}`
    );
  }

  try {
    console.log('[API Client] Sending prediction request:', request);

    const response = await fetchWithTimeout(
      url,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      },
      timeout
    );

    console.log('[API Client] Response status:', response.status);

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const detail = errorData.detail || `Server error (HTTP ${response.status})`;

      // Determine error type
      let errorType: APIError['type'] = 'server';
      if (response.status === 400) {
        errorType = 'validation';
      } else if (response.status >= 500) {
        errorType = 'server';
      }

      console.error('[API Client] Server error:', { status: response.status, detail });

      const error = new Error(detail) as Error & { type: APIError['type']; status: number };
      error.type = errorType;
      error.status = response.status;
      throw error;
    }

    const data: AlloyPredictionResponse = await response.json();
    console.log('[API Client] Prediction successful');
    return data;

  } catch (error: any) {
    // Timeout error
    if (error.message === 'timeout') {
      console.error('[API Client] Request timeout');
      const timeoutError = new Error(
        `Request timeout after ${timeout / 1000} seconds. ` +
        'The prediction service is taking too long to respond. Please try again.'
      ) as Error & { type: APIError['type'] };
      timeoutError.type = 'timeout';
      throw timeoutError;
    }

    // Network error (no response from server)
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      console.error('[API Client] Network error');
      const networkError = new Error(
        'Unable to connect to the prediction service. ' +
        'Please check your internet connection or try again later. ' +
        `(Backend: ${baseURL})`
      ) as Error & { type: APIError['type'] };
      networkError.type = 'network';
      throw networkError;
    }

    // Re-throw with error type if not already set
    if (!error.type) {
      error.type = 'server';
    }
    throw error;
  }
}

/**
 * Health check
 *
 * @returns Promise with health status
 */
export async function checkHealth(): Promise<{ status: string; version?: string }> {
  const url = `${baseURL}/health`;

  try {
    const response = await fetchWithTimeout(url, {}, 5000); // 5s timeout for health check

    if (!response.ok) {
      throw new Error(`Health check failed (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('[API Client] Health check failed:', error.message);
    throw error;
  }
}

/**
 * Get available models
 *
 * @returns Promise with list of available models
 */
export async function getAvailableModels(): Promise<ModelsResponse> {
  const url = `${baseURL}/api/v1/predict/models`;

  try {
    const response = await fetchWithTimeout(url, {}, 5000);

    if (!response.ok) {
      throw new Error(`Failed to fetch models (HTTP ${response.status})`);
    }

    const data = await response.json();
    console.log('[API Client] Available models:', data.models.map((m: any) => m.name).join(', '));
    return data;
  } catch (error: any) {
    console.error('[API Client] Failed to get models:', error.message);
    throw error;
  }
}

/**
 * Get version information
 *
 * @returns Promise with version info
 */
export async function getVersionInfo(): Promise<any> {
  const url = `${baseURL}/version`;

  try {
    const response = await fetchWithTimeout(url, {}, 5000);

    if (!response.ok) {
      throw new Error(`Failed to fetch version info (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (error: any) {
    console.warn('[API Client] Failed to get version info:', error.message);
    return null; // Non-critical, return null
  }
}

// Export base URL for reference
export { baseURL as API_BASE_URL };
export { DEFAULT_TIMEOUT };
