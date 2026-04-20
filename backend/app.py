from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "ambushvision")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


@app.route("/")
def home():
    return jsonify({"message": "Ambush Vision backend is running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/items", methods=["GET"])
def get_items():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id, text FROM items ORDER BY id DESC;")
        items = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(items), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/items", methods=["POST"])
def create_item():
    try:
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "INSERT INTO items (text) VALUES (%s) RETURNING id, text;",
            (text,)
        )
        new_item = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(new_item), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sentiment", methods=["POST"])
def sentiment():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        lowered = text.lower()

        positive_words = ["happy", "great", "good", "amazing", "love", "excited"]
        negative_words = ["bad", "sad", "angry", "upset", "frustrated", "hate"]

        positive_score = sum(word in lowered for word in positive_words)
        negative_score = sum(word in lowered for word in negative_words)

        if positive_score > negative_score:
            result = "POSITIVE"
        elif negative_score > positive_score:
            result = "NEGATIVE"
        else:
            result = "NEUTRAL"

        return jsonify({"sentiment": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/image", methods=["POST"])
def image_analysis():
    try:
        return jsonify({
            "labels": ["Sample Label 1", "Sample Label 2", "Sample Label 3"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)