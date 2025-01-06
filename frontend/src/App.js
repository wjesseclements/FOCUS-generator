import React, { useState } from "react";
import axios from "axios";
import Tippy from "@tippyjs/react";
import "tippy.js/dist/tippy.css"; // Tippy's default styles

export default function App() {
  const [selectedProfile, setSelectedProfile] = useState(""); // No default selection
  const [distribution, setDistribution] = useState(""); // No default selection
  const [response, setResponse] = useState(null); // Stores the response
  const [isReset, setIsReset] = useState(false); // Tracks whether the button is in "Reset" mode

  const generateCUR = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/generate-cur", {
        profile: selectedProfile,
        distribution: distribution || "Evenly Distributed", // Default to "Evenly Distributed" if none selected
      });
      setResponse(res.data);
      setIsReset(true); // Switch button to Reset mode
    } catch (error) {
      console.error("Error generating CUR:", error);
    }
  };

  const resetSelections = () => {
    setSelectedProfile("");
    setDistribution("");
    setResponse(null);
    setIsReset(false); // Revert button to Generate CUR mode
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

      {/* Generate/Reset Button */}
      <div className="text-center">
        <button
          onClick={isReset ? resetSelections : generateCUR}
          className={`px-6 py-2 rounded shadow ${
            isReset
              ? "bg-red-600 text-white hover:bg-red-700"
              : selectedProfile && distribution
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-gray-400 text-gray-700 cursor-not-allowed"
          }`}
          disabled={!selectedProfile || !distribution}
        >
          {isReset ? "Reset" : "Generate CUR"}
        </button>
      </div>

      {/* Display Response */}
      {response && (
        <div className="mt-6 text-center">
          <a
            href={response.url}
            className="text-blue-700 underline"
            download
          >
            Download CUR
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