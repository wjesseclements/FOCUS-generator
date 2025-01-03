import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [rowCount, setRowCount] = useState(10); // State for row_count
  const [response, setResponse] = useState(null); // State for the response

  const generateCUR = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/generate-cur", {
        row_count: parseInt(rowCount, 10), // Ensure rowCount is sent as an integer
      });
      setResponse(res.data);
    } catch (error) {
      console.error("Error generating CUR:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-blue-100 text-blue-800">
      <h1 className="text-4xl font-bold mb-4">Generate CUR</h1>
      
      {/* Input for row count */}
      <div className="mb-4">
        <label htmlFor="rowCount" className="block text-lg font-medium mb-2">
          Number of Rows:
        </label>
        <input
          id="rowCount"
          type="number"
          value={rowCount}
          onChange={(e) => setRowCount(e.target.value)}
          className="p-2 border rounded"
        />
      </div>

      {/* Button to generate CUR */}
      <button
        onClick={generateCUR}
        className="px-4 py-2 bg-blue-500 text-white rounded shadow hover:bg-blue-600"
      >
        Generate CUR
      </button>

      {/* Display the response */}
      {response && (
        <div className="mt-4 text-center">
          <p className="text-lg font-medium">{response.message}</p>
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
  );
}