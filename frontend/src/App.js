import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [selectedProfile, setSelectedProfile] = useState("");
  const [distribution, setDistribution] = useState("Evenly Distributed");
  const [response, setResponse] = useState(null);

  const generateCUR = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/generate-cur", {
        profile: selectedProfile,
        distribution: distribution,
      });
      setResponse(res.data);
    } catch (error) {
      console.error("Error generating CUR:", error);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 flex flex-col items-center">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white py-10 px-4 text-center w-full">
        <h1 className="text-5xl font-bold mb-2">FOCUS CUR Generator</h1>
        <p className="text-lg">
          Quickly generate synthetic FOCUS-conformed Cost and Usage Reports for
          your testing and FinOps needs.
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="flex justify-center items-center mt-6">
        <div
          className={`w-1/3 h-2 ${
            selectedProfile ? "bg-blue-600" : "bg-gray-300"
          } mx-1`}
        ></div>
        <div
          className={`w-1/3 h-2 ${
            distribution ? "bg-blue-600" : "bg-gray-300"
          } mx-1`}
        ></div>
        <div
          className={`w-1/3 h-2 ${response ? "bg-blue-600" : "bg-gray-300"} mx-1`}
        ></div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl w-full mt-10 px-4">
        {/* T-Shirt Size Selection */}
        <div className="mb-6 text-center">
          <p className="text-lg font-medium mb-4">Select a T-Shirt Size:</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: "Greenfield", description: "$20,000 - $50,000 / month" },
              { name: "Large Business", description: "$100,000 - $250,000 / month" },
              { name: "Enterprise", description: "$1,000,000+ / month" },
            ].map((profile) => (
              <div
                key={profile.name}
                onClick={() => setSelectedProfile(profile.name)}
                className={`p-6 rounded shadow-lg border ${
                  selectedProfile === profile.name
                    ? "border-blue-600 bg-blue-100"
                    : "bg-white hover:bg-gray-100"
                } cursor-pointer`}
              >
                <h2 className="text-xl font-bold">{profile.name}</h2>
                <p className="text-sm text-gray-600">{profile.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Distribution Selection */}
        <div className="mb-6 text-center">
          <p className="text-lg font-medium mb-4">Select Distribution:</p>
          <div className="flex flex-wrap justify-center gap-4">
            {["Evenly Distributed", "ML Focused", "Data Intensive", "Media Intensive"].map(
              (dist) => (
                <button
                  key={dist}
                  onClick={() => setDistribution(dist)}
                  className={`px-4 py-2 rounded shadow ${
                    distribution === dist
                      ? "bg-blue-600 text-white"
                      : "bg-white text-blue-600 border border-blue-600 hover:bg-blue-100"
                  }`}
                >
                  {dist}
                </button>
              )
            )}
          </div>
        </div>

        {/* Generate Button */}
        <div className="text-center">
          <button
            onClick={generateCUR}
            className="px-6 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700"
            disabled={!selectedProfile}
          >
            Generate CUR
          </button>
        </div>

        {/* Display Response */}
        {response && (
          <div className="mt-6 text-center">
            <p className="text-lg font-medium mb-2">{response.message}</p>
            <a
              href={response.url}
              className="text-blue-700 underline"
              download
            >
              Download CUR
            </a>
          </div>
        )}
      </div>
    </div>
  );
}