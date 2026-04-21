import { useState } from "react";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [text, setText] = useState("");
  const [sentimentResult, setSentimentResult] = useState("");
  const [items, setItems] = useState([]);
  const [imageLabels, setImageLabels] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  const API_BASE_URL = "http://52.90.143.126:5001";

  const handleLogin = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (data.token) {
        localStorage.setItem("token", data.token);
        alert("Login successful!");
      } else {
        alert(data.message || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Login failed");
    }
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem("token");

      const res = await fetch(`${API_BASE_URL}/items`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || data.error || "Save failed");
        return;
      }

      console.log(data);
      alert("Saved!");
    } catch (error) {
      console.error("Save error:", error);
      alert("Save failed");
    }
  };

  const handleGetItems = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/items`);
      const data = await res.json();
      setItems(data);
    } catch (error) {
      console.error("Get items error:", error);
    }
  };

  const handleSentiment = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/sentiment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();
      setSentimentResult(data.sentiment || "No result");
    } catch (error) {
      console.error("Sentiment error:", error);
      setSentimentResult("Error");
    }
  };

  const handleImageChange = (e) => {
    setSelectedImage(e.target.files[0]);
  };

  const handleImageUpload = async () => {
    try {
      if (!selectedImage) {
        alert("Please choose an image first.");
        return;
      }

      const formData = new FormData();
      formData.append("image", selectedImage);

      const res = await fetch(`${API_BASE_URL}/image-upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Image upload failed");
        return;
      }

      setImageLabels(data.labels || []);
    } catch (error) {
      console.error("Image upload error:", error);
      alert("Image upload failed");
    }
  };

  return (
    <div className="app-container">
      <div className="app-card">
        <h1>Ambush Vision CI/CD</h1>
        <p className="subtitle">
          A three-tier application using React, Flask, PostgreSQL, Docker,
          Docker Compose, GitHub Actions, AWS Comprehend, AWS Rekognition, and S3.
        </p>

        <div className="section">
          <h2>Login</h2>

          <input
            className="text-input"
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            className="text-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div className="button-group">
            <button onClick={handleLogin}>Login</button>
          </div>
        </div>

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

          <input type="file" accept="image/*" onChange={handleImageChange} />

          <div className="button-group">
            <button onClick={handleImageUpload}>Upload & Analyze Image</button>
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