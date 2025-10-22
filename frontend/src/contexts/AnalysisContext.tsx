import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { AnalysisResult, AnalysisStatus, AnalysisRequest, AnalysisHistory } from '../types';

// State interface
interface AnalysisState {
  currentAnalysis: AnalysisResult | null;
  analysisStatus: AnalysisStatus | null;
  history: AnalysisHistory[];
  isLoading: boolean;
  error: string | null;
}

// Action types
type AnalysisAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_ANALYSIS_STATUS'; payload: AnalysisStatus }
  | { type: 'SET_CURRENT_ANALYSIS'; payload: AnalysisResult }
  | { type: 'SET_HISTORY'; payload: AnalysisHistory[] }
  | { type: 'CLEAR_CURRENT_ANALYSIS' }
  | { type: 'ADD_TO_HISTORY'; payload: AnalysisHistory };

// Context interface
interface AnalysisContextType {
  state: AnalysisState;
  startAnalysis: (request: AnalysisRequest) => Promise<string>;
  getAnalysisStatus: (taskId: string) => Promise<void>;
  getAnalysisResult: (taskId: string) => Promise<void>;
  getHistory: () => Promise<void>;
  clearCurrentAnalysis: () => void;
  deleteAnalysis: (taskId: string) => Promise<void>;
}

// Initial state
const initialState: AnalysisState = {
  currentAnalysis: null,
  analysisStatus: null,
  history: [],
  isLoading: false,
  error: null,
};

// Reducer
function analysisReducer(state: AnalysisState, action: AnalysisAction): AnalysisState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'SET_ANALYSIS_STATUS':
      return { ...state, analysisStatus: action.payload };
    case 'SET_CURRENT_ANALYSIS':
      return { ...state, currentAnalysis: action.payload, isLoading: false };
    case 'SET_HISTORY':
      return { ...state, history: action.payload };
    case 'CLEAR_CURRENT_ANALYSIS':
      return { ...state, currentAnalysis: null, analysisStatus: null };
    case 'ADD_TO_HISTORY':
      return { 
        ...state, 
        history: [action.payload, ...state.history.slice(0, 9)] // Keep only 10 recent items
      };
    default:
      return state;
  }
}

// Create context
const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

// Provider component
export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  // API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Helper function for API calls
  const apiCall = useCallback(async (endpoint: string, options?: RequestInit) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  }, [API_BASE_URL]);

  // Start analysis
  const startAnalysis = useCallback(async (request: AnalysisRequest): Promise<string> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await apiCall('/analyze', {
        method: 'POST',
        body: JSON.stringify(request),
      });

      const taskId = response.task_id;
      
      // Start polling for status
      const pollStatus = async (): Promise<boolean> => {
        try {
          const status = await apiCall(`/status/${taskId}`);
          dispatch({ type: 'SET_ANALYSIS_STATUS', payload: status });
          return status.status === 'completed' || status.status === 'failed';
        } catch (error) {
          console.error('Error polling status:', error);
          return false;
        }
      };

      // Poll every 2 seconds
      const pollInterval = setInterval(async () => {
        const isComplete = await pollStatus();
        
        if (isComplete) {
          clearInterval(pollInterval);
          // Get the latest status to determine action
          try {
            const finalStatus = await apiCall(`/status/${taskId}`);
            if (finalStatus.status === 'completed') {
              const result = await apiCall(`/result/${taskId}`);
              dispatch({ type: 'SET_CURRENT_ANALYSIS', payload: result });
              
              // Add to history
              const historyItem: AnalysisHistory = {
                task_id: result.task_id,
                query: result.query,
                total_posts: result.total_posts,
                total_comments: result.total_comments,
                analysis_duration: result.analysis_duration,
                created_at: result.created_at,
              };
              dispatch({ type: 'ADD_TO_HISTORY', payload: historyItem });
            } else {
              dispatch({ type: 'SET_ERROR', payload: 'Analysis failed' });
            }
          } catch (error) {
            dispatch({ type: 'SET_ERROR', payload: 'Failed to get analysis result' });
          }
        }
      }, 2000);

      return taskId;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    }
  }, [apiCall]);

  // Get analysis status
  const getAnalysisStatus = useCallback(async (taskId: string) => {
    try {
      const status = await apiCall(`/status/${taskId}`);
      dispatch({ type: 'SET_ANALYSIS_STATUS', payload: status });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  }, [apiCall]);

  // Get analysis result
  const getAnalysisResult = useCallback(async (taskId: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const result = await apiCall(`/result/${taskId}`);
      dispatch({ type: 'SET_CURRENT_ANALYSIS', payload: result });
      
      // Add to history
      const historyItem: AnalysisHistory = {
        task_id: result.task_id,
        query: result.query,
        total_posts: result.total_posts,
        total_comments: result.total_comments,
        analysis_duration: result.analysis_duration,
        created_at: result.created_at,
      };
      dispatch({ type: 'ADD_TO_HISTORY', payload: historyItem });
      
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  }, [apiCall]);

  // Get history
  const getHistory = useCallback(async () => {
    try {
      const response = await apiCall('/history');
      dispatch({ type: 'SET_HISTORY', payload: response.history });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  }, [apiCall]);

  // Clear current analysis
  const clearCurrentAnalysis = useCallback(() => {
    dispatch({ type: 'CLEAR_CURRENT_ANALYSIS' });
  }, []);

  // Delete analysis
  const deleteAnalysis = useCallback(async (taskId: string) => {
    try {
      await apiCall(`/result/${taskId}`, { method: 'DELETE' });
      
      // Update history
      const updatedHistory = state.history.filter(item => item.task_id !== taskId);
      dispatch({ type: 'SET_HISTORY', payload: updatedHistory });
      
      // Clear current analysis if it's the one being deleted
      if (state.currentAnalysis?.task_id === taskId) {
        dispatch({ type: 'CLEAR_CURRENT_ANALYSIS' });
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  }, [apiCall, state.history, state.currentAnalysis?.task_id]);

  const value: AnalysisContextType = {
    state,
    startAnalysis,
    getAnalysisStatus,
    getAnalysisResult,
    getHistory,
    clearCurrentAnalysis,
    deleteAnalysis,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
}

// Hook to use the context
export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
}