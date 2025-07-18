import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Configure axios defaults
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRF-Token';

// Add request interceptor to include CSRF token
axios.interceptors.request.use(
  (config) => {
    // Get CSRF token from cookie or header
    const token = getCsrfToken();
    if (token) {
      config.headers['X-CSRF-Token'] = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle CSRF token updates
axios.interceptors.response.use(
  (response) => {
    // Update CSRF token if provided in response
    const newToken = response.headers['x-csrf-token'];
    if (newToken) {
      setCsrfToken(newToken);
    }
    return response;
  },
  (error) => {
    // Handle CSRF token errors
    if (error.response?.status === 403 && error.response?.data?.error?.includes('CSRF')) {
      toast.error('Security Error', {
        description: 'Please refresh the page and try again.',
        duration: 5000
      });
    }
    return Promise.reject(error);
  }
);

// Helper functions for CSRF token management
function getCsrfToken() {
  // Try to get from cookie first
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return decodeURIComponent(value);
    }
  }
  
  // Try to get from localStorage as fallback
  return localStorage.getItem('csrftoken');
}

function setCsrfToken(token) {
  // Store in localStorage as fallback
  localStorage.setItem('csrftoken', token);
}

export const useFocusGenerator = () => {
  const [selectedProfile, setSelectedProfile] = useState("");
  const [distribution, setDistribution] = useState("");
  const [rowCount, setRowCount] = useState(20);
  const [response, setResponse] = useState(null);
  const [isReset, setIsReset] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch CSRF token on component mount
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        await axios.get(`${API_URL}/health`);
      } catch (error) {
        console.warn('Failed to fetch CSRF token:', error);
      }
    };
    
    fetchCsrfToken();
  }, []);

  const generateCUR = async (providers = [], trendOptions = null, multiMonth = false) => {
    if (!selectedProfile || !distribution) {
      toast.error("Please select both a profile and distribution");
      return;
    }
    
    if (providers.length === 0) {
      toast.error("Please select at least one cloud provider");
      return;
    }

    try {
      setIsLoading(true);
      const loadingMessage = multiMonth ? "Generating trend data..." : "Generating FOCUS CUR...";
      toast.loading(loadingMessage, { id: "generating" });
      
      const requestData = {
        profile: selectedProfile,
        distribution: distribution || "Evenly Distributed",
        row_count: parseInt(rowCount, 10),
        providers: providers,
        multi_month: multiMonth
      };
      
      if (multiMonth && trendOptions) {
        requestData.trend_options = trendOptions;
      }
      
      const res = await axios.post(`${API_URL}/generate-cur`, requestData);
      
      setResponse(res.data);
      setIsReset(true);
      setIsLoading(false);
      
      const successMessage = multiMonth 
        ? "Trend data generated successfully!" 
        : "CUR generated successfully!";
      const description = multiMonth
        ? `Your multi-month FOCUS dataset is ready for download.`
        : `Your ${rowCount}-row FOCUS report is ready for download.`;
        
      toast.success(successMessage, { 
        id: "generating",
        description: description
      });
    } catch (error) {
      console.error("Error generating CUR:", error);
      setIsLoading(false);
      
      let errorMessage = "Error generating CUR. Please try again.";
      
      if (error.response) {
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = "Network error: Unable to connect to the server. Please check if the API is running.";
      }
      
      toast.error("Generation Failed", {
        id: "generating",
        description: errorMessage
      });
    }
  };

  const resetSelections = () => {
    setSelectedProfile("");
    setDistribution("");
    setRowCount(20);
    setResponse(null);
    setIsReset(false);
    toast.info("Selections reset", {
      description: "You can now make new selections."
    });
  };

  const handleRowCountChange = (value) => {
    if (value === "" || /^[1-9][0-9]*$/.test(value)) {
      setRowCount(value);
    }
  };

  return {
    selectedProfile,
    setSelectedProfile,
    distribution,
    setDistribution,
    rowCount,
    setRowCount,
    handleRowCountChange,
    response,
    isReset,
    isLoading,
    generateCUR,
    resetSelections
  };
};