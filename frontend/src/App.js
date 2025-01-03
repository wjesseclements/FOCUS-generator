import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [response, setResponse] = useState(null);
  const [rowCount, setRowCount] = useState(20); // Default row count

  const generateCUR = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/generate-cur", {
        row_count: rowCount,
      });
      setResponse(res.data);
    } catch (error) {
      console.error("Error generating CUR:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-blue-100 text-blue-800">
      <h1 className="text-4xl font-bold mb-4">Generate CUR</h1>
      <div className="flex items-center mb-4">
        <label className="mr-2">Row Count:</label>
        <input
          type="number"
          value={rowCount}
          onChange={(e) => setRowCount(Number(e.target.value))}
          className="border p-2 rounded"
        />
      </div>
      <button
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={generateCUR}
      >
        Generate CUR
      </button>
      {response && (
        <div className="mt-4">
          <p>{response.message}</p>
          <a
            href={response.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-700 underline"
          >
            Download CUR
          </a>
        </div>
      )}
    </div>
  );
}