import React, { useState } from "react";
import axios from "axios";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css"; // Tippy's default styles

// Get API URL from environment variables
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function App() {
  const [selectedProfile, setSelectedProfile] = useState(""); // No default selection
  const [distribution, setDistribution] = useState(""); // No default selection
  const [rowCount, setRowCount] = useState(20); // Default to 20 rows
  const [response, setResponse] = useState(null); // Stores the response
  const [isReset, setIsReset] = useState(false); // Tracks whether the button is in "Reset" mode
  const [isLoading, setIsLoading] = useState(false); // Tracks loading state

  const generateCUR = async () => {
    try {
      setIsLoading(true);
      const res = await axios.post(`${API_URL}/generate-cur`, {
        profile: selectedProfile,
        distribution: distribution || "Evenly Distributed", // Default to "Evenly Distributed" if none selected
        row_count: parseInt(rowCount, 10) // Convert to integer and send to API
      });
      setResponse(res.data);
      setIsReset(true); // Switch button to Reset mode
      setIsLoading(false);
    } catch (error) {
      console.error("Error generating CUR:", error);
      setIsLoading(false);
      
      // More specific error handling
      if (error.response) {
        // Server responded with error status
        const message = error.response.data?.detail || `Server error: ${error.response.status}`;
        alert(`Error: ${message}`);
      } else if (error.request) {
        // Request was made but no response received
        alert("Network error: Unable to connect to the server. Please check if the API is running.");
      } else {
        // Something else happened
        alert("Error generating CUR. Please try again.");
      }
    }
  };

  const resetSelections = () => {
    setSelectedProfile("");
    setDistribution("");
    setRowCount(20); // Reset to default
    setResponse(null);
    setIsReset(false); // Revert button to Generate CUR mode
  };
  
  // Handle row count change with validation
  const handleRowCountChange = (e) => {
    const value = e.target.value;
    // Only allow positive integers
    if (value === "" || /^[1-9][0-9]*$/.test(value)) {
      setRowCount(value);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 flex flex-col items-center pb-16">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-10 px-4 text-center w-full">
        <h1 className="text-5xl font-bold mb-2">FOCUS CUR Generator</h1>
        <p className="text-lg">
          Quickly generate synthetic FOCUS-conformed Cost and Usage Reports for
          your testing and FinOps needs.
        </p>
      </div>

      {/* Profile Selection with Tooltips */}
      <div className="my-6 text-center">
        <p className="text-lg font-medium mb-4">Select Profile:</p>
        <div className="flex flex-wrap justify-center gap-4">
          {[
            {
              name: "Greenfield",
              description: "For startups or small businesses ($20k–$50k/month).",
            },
            {
              name: "Large Business",
              description:
                "For medium-sized organizations ($100k–$250k/month).",
            },
            {
              name: "Enterprise",
              description: "For large corporations ($1M+/month).",
            },
          ].map((profile) => (
            <Tippy content={profile.description} key={profile.name} arrow={true}>
              <button
                onClick={() => setSelectedProfile(profile.name)}
                className={`px-4 py-2 rounded shadow ${
                  selectedProfile === profile.name
                    ? "bg-blue-600 text-white"
                    : "bg-white text-blue-600 border border-blue-600 hover:bg-blue-100"
                }`}
              >
                {profile.name}
              </button>
            </Tippy>
          ))}
        </div>
      </div>

      {/* Distribution Selection with Tooltips */}
      <div className="mb-6 text-center">
        <p className="text-lg font-medium mb-4">Select Distribution:</p>
        <div className="flex flex-wrap justify-center gap-4">
          {[
            { name: "Evenly Distributed", description: "Evenly spread across services." },
            { name: "ML-Focused", description: "Emphasizing SageMaker and ML workloads." },
            { name: "Data-Intensive", description: "Focus on S3, Redshift, and data-heavy services." },
            { name: "Media-Intensive", description: "Optimized for high storage and bandwidth needs." },
          ].map((dist) => (
            <Tippy content={dist.description} key={dist.name} arrow={true}>
              <button
                onClick={() => setDistribution(dist.name)}
                className={`px-4 py-2 rounded shadow ${
                  distribution === dist.name
                    ? "bg-blue-600 text-white"
                    : "bg-white text-blue-600 border border-blue-600 hover:bg-blue-100"
                }`}
              >
                {dist.name}
              </button>
            </Tippy>
          ))}
        </div>
      </div>

      {/* Row Count Input */}
      <div className="mb-6 text-center">
        <p className="text-lg font-medium mb-4">Number of Rows to Generate:</p>
        <div className="flex justify-center">
          <Tippy content="Higher values will generate more data but may take longer to process" arrow={true}>
            <div className="relative">
              <input
                type="number"
                min="1"
                max="1000"
                value={rowCount}
                onChange={handleRowCountChange}
                className="w-32 px-4 py-2 rounded border border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <span className="text-gray-500">rows</span>
              </div>
            </div>
          </Tippy>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Recommended: 20-100 rows for quick generation, 100-500 for more comprehensive data
        </p>
      </div>

      {/* Generate/Reset Button */}
      <div className="text-center">
        <button
          onClick={isReset ? resetSelections : generateCUR}
          className={`px-6 py-2 rounded shadow ${
            isLoading
              ? "bg-gray-500 text-white cursor-wait"
              : isReset
              ? "bg-red-600 text-white hover:bg-red-700"
              : selectedProfile && distribution
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-gray-400 text-gray-700 cursor-not-allowed"
          }`}
          disabled={!selectedProfile || !distribution || isLoading}
        >
          {isLoading ? "Generating..." : isReset ? "Reset" : "Generate CUR"}
        </button>
      </div>

      {/* Display Response */}
      {response && (
        <div className="mt-6 text-center">
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <p className="font-bold">Success!</p>
            <p>{response.message}</p>
          </div>
          <a
            href={response.url}
            className="text-blue-700 underline text-lg font-semibold hover:text-blue-900"
            download
          >
            Download CUR ({rowCount} rows)
          </a>
        </div>
      )}

      {/* Footer Section */}
      <footer className="bg-gray-800 text-gray-300 py-4 text-center fixed bottom-0 w-full">
        <p className="text-sm">
          Disclaimer: This data is not real and is only intended for testing
          purposes. This website is not affiliated with AWS or the FinOps
          Foundation.
        </p>
      </footer>
    </div>
  );
}