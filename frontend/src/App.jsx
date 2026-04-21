import { useState } from "react";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  const [sentimentResult, setSentimentResult] = useState("");
  const [items, setItems] = useState([]);
  const [imageLabels, setImageLabels] = useState([]);

  const API_BASE_URL = "http://localhost:5001";

  const handleSave = async () => {
    const res = await fetch(`${API_BASE_URL}/items`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    console.log(data);
    alert("Saved!");
  };

  const handleGetItems = async () => {
    const res = await fetch(`${API_BASE_URL}/items`);
    const data = await res.json();
    setItems(data);
  };

  const handleSentiment = async () => {
    const res = await fetch(`${API_BASE_URL}/sentiment`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();
    setSentimentResult(data.sentiment);
  };

  const handleImage = async () => {
    const res = await fetch(`${API_BASE_URL}/image`, {
      method: "POST",
    });

    const data = await res.json();
    setImageLabels(data.labels || []);
  };

  return (
    <div className="app-container">
      <div className="app-card">
        <h1>Ambush Vision CI/CD</h1>
        <p className="subtitle">
          A three-tier application using React, Flask, PostgreSQL, Docker,
          Docker Compose, and GitHub Actions.
        </p>

        <div className="section">
          <h2>Text Analysis & Storage</h2>

          <input
            className="text-input"
            type="text"
            placeholder="Enter text here"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <div className="button-group">
            <button onClick={handleSave}>Save to DB</button>
            <button onClick={handleGetItems}>Get Items</button>
            <button onClick={handleSentiment}>Analyze Sentiment</button>
          </div>

          <div className="result-box">
            <h3>Sentiment Result</h3>
            <p>{sentimentResult || "No sentiment analyzed yet."}</p>
          </div>

          <div className="result-box">
            <h3>Saved Items</h3>
            {items.length > 0 ? (
              <ul>
                {items.map((item) => (
                  <li key={item.id}>{item.text}</li>
                ))}
              </ul>
            ) : (
              <p>No saved items yet.</p>
            )}
          </div>
        </div>

        <div className="section">
          <h2>Image Analysis</h2>

          <div className="button-group">
            <button onClick={handleImage}>Analyze Image</button>
          </div>

          <div className="result-box">
            <h3>Image Labels</h3>
            {imageLabels.length > 0 ? (
              <ul>
                {imageLabels.map((label, index) => (
                  <li key={index}>{label}</li>
                ))}
              </ul>
            ) : (
              <p>No image analyzed yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;