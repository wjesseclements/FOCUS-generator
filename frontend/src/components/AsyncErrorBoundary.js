import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

/**
 * AsyncErrorBoundary - Handles async errors and provides retry functionality
 * This is a functional component that wraps async operations
 */
const AsyncErrorBoundary = ({ 
  children, 
  fallback, 
  onError,
  retryDelay = 1000,
  maxRetries = 3 
}) => {
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  useEffect(() => {
    // Global error handler for unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      // Only handle if this is likely related to our component
      if (event.reason && typeof event.reason === 'object') {
        setError(event.reason);
        
        // Show user-friendly error
        toast.error('Network Error', {
          description: 'Failed to connect to the server. Please check your internet connection.',
          duration: 5000
        });
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  const handleRetry = async () => {
    if (retryCount >= maxRetries) {
      toast.error('Max retries reached', {
        description: 'Please refresh the page or try again later.',
        duration: 5000
      });
      return;
    }

    setIsRetrying(true);
    setRetryCount(prev => prev + 1);

    try {
      // Wait for retry delay
      await new Promise(resolve => setTimeout(resolve, retryDelay));
      
      // Clear error to trigger re-render
      setError(null);
      
      // Call custom error handler if provided
      if (onError) {
        await onError(error);
      }
      
      toast.success('Retrying...', {
        description: 'Attempting to recover from the error.',
        duration: 2000
      });
      
    } catch (retryError) {
      console.error('Retry failed:', retryError);
      setError(retryError);
      
      toast.error('Retry failed', {
        description: 'The operation failed again. Please try refreshing the page.',
        duration: 5000
      });
    } finally {
      setIsRetrying(false);
    }
  };

  const handleReset = () => {
    setError(null);
    setRetryCount(0);
    setIsRetrying(false);
  };

  // If there's an error, show fallback UI
  if (error) {
    // Use custom fallback if provided
    if (fallback) {
      return fallback({ error, retry: handleRetry, reset: handleReset, isRetrying });
    }

    // Default fallback UI
    return (
      <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <div className="flex items-center mb-4">
          <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-red-800 dark:text-red-200 font-medium">
            Operation Failed
          </h3>
        </div>
        
        <p className="text-red-700 dark:text-red-300 mb-4">
          {error.message || 'An unexpected error occurred while processing your request.'}
        </p>
        
        <div className="flex gap-2">
          <button
            onClick={handleRetry}
            disabled={isRetrying || retryCount >= maxRetries}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
          >
            {isRetrying ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Retrying...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Retry ({retryCount}/{maxRetries})
              </>
            )}
          </button>
          
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
          >
            Reset
          </button>
        </div>
      </div>
    );
  }

  // Render children normally
  return children;
};

/**
 * Hook for handling async errors in functional components
 */
export const useAsyncError = () => {
  const [error, setError] = useState(null);
  
  const throwAsyncError = (error) => {
    setError(error);
    // Re-throw to trigger error boundary
    throw error;
  };
  
  return { error, throwAsyncError };
};

/**
 * HOC for wrapping components with async error handling
 */
export const withAsyncErrorHandling = (Component, errorBoundaryProps = {}) => {
  return function WrappedComponent(props) {
    return (
      <AsyncErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </AsyncErrorBoundary>
    );
  };
};

export default AsyncErrorBoundary;