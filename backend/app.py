from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import boto3
import jwt
import datetime
from functools import wraps
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "ambushvision")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "")

comprehend = boto3.client("comprehend", region_name=AWS_REGION)
rekognition = boto3.client("rekognition", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except Exception as e:
            return jsonify({"message": "Token is invalid", "error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated


@app.route("/")
def home():
    return jsonify({"message": "Ambush Vision backend is running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # simple demo login
    if username == "admin" and password == "password123":
        token = jwt.encode(
            {
                "user": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


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
@token_required
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

        response = comprehend.detect_sentiment(
            Text=text,
            LanguageCode="en"
        )

        return jsonify({
            "sentiment": response["Sentiment"],
            "scores": response["SentimentScore"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/image-upload", methods=["POST"])
def image_upload():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        if not S3_BUCKET:
            return jsonify({"error": "S3 bucket not configured"}), 500

        s3_key = f"uploads/{file.filename}"
        s3.upload_fileobj(file, S3_BUCKET, s3_key)

        response = rekognition.detect_labels(
            Image={
                "S3Object": {
                    "Bucket": S3_BUCKET,
                    "Name": s3_key
                }
            },
            MaxLabels=10
        )

        labels = [label["Name"] for label in response["Labels"]]

        return jsonify({
            "message": "Image uploaded successfully",
            "s3_key": s3_key,
            "labels": labels
        }), 200

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