import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const useFocusGenerator = () => {
  const [selectedProfile, setSelectedProfile] = useState("");
  const [distribution, setDistribution] = useState("");
  const [rowCount, setRowCount] = useState(20);
  const [response, setResponse] = useState(null);
  const [isReset, setIsReset] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

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