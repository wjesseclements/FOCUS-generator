import React, { useEffect, useState } from "react";
import axios from "axios";

export default function App() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // Fetch data from the API
    axios
      .get("https://jsonplaceholder.typicode.com/posts")
      .then((response) => {
        setPosts(response.data); // Store the API data in state
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-blue-100 text-blue-800">
      <h1 className="text-4xl font-bold mb-4">Axios Example</h1>
      <ul className="w-full max-w-md">
        {posts.slice(0, 5).map((post) => (
          <li key={post.id} className="bg-white p-4 mb-2 rounded shadow">
            <h2 className="text-xl font-semibold">{post.title}</h2>
            <p>{post.body}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}