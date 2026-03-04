# ===========================
# app.py (FIXED & WORKING)
# ===========================

from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- DATABASE (SAFE IMPORT) ----------------
try:
    from database import db, users_col, history_col, images_col
except:
    db = users_col = history_col = images_col = None

# ---------------- APP INIT ----------------
app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ---------------- AI CONFIG ----------------
CLIPDROP_API_KEY = os.getenv("AI_API_KEY")

# Print status for easier local debugging (doesn't reveal secret)
if CLIPDROP_API_KEY:
    app.logger.info("AI_API_KEY is set. Image generation should work.")
else:
    # Do not crash the app at startup — warn and return a clear error from the endpoint
    app.logger.warning("AI_API_KEY (ClipDrop) is not set. Image generation will return an error until configured.")
    print("WARNING: AI_API_KEY is not set. Image generation will fail until you set AI_API_KEY in your environment or .env file.")

# ---------------- ENSURE FOLDER EXISTS ----------------
os.makedirs("static/generated", exist_ok=True)

# ---------------- HEALTH CHECK ----------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# ---------------- LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    token = create_access_token(identity=email)
    return jsonify({"access_token": token}), 200

# ---------------- IMAGE GENERATION ----------------
# Dedicated OPTIONS handler so browser preflight isn't blocked by JWT decorator
@app.route("/api/generate", methods=["OPTIONS"])
def generate_image_options():
    return jsonify({"status": "ok"}), 200

@app.route("/api/generate", methods=["POST"])
@jwt_required()
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        style = data.get("style", "realistic")

        # Log request for debugging
        app.logger.info(f"/api/generate called with prompt={prompt!r}, style={style!r}")
        print(f"/api/generate called with prompt={prompt!r}, style={style!r}")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        email = get_jwt_identity()

        # ---------------- CLIPDROP API ----------------
        if not CLIPDROP_API_KEY:
            app.logger.error("AI_API_KEY missing — returning 500")
            print("ERROR: AI_API_KEY not configured on server. Set AI_API_KEY in .env or environment.")
            return jsonify({"error": "AI_API_KEY not configured on server. Please set AI_API_KEY in .env"}), 500

        headers = {
            "x-api-key": CLIPDROP_API_KEY
        }

        files = {
            "prompt": (None, f"{prompt}, {style} style"),
        }

        response = requests.post(
            "https://clipdrop-api.co/text-to-image/v1",
            headers=headers,
            files=files,
            timeout=60
        )

        if response.status_code != 200:
            # Log ClipDrop error details for debugging
            app.logger.error(f"ClipDrop API error {response.status_code}: {response.text}")
            print(f"ClipDrop API error {response.status_code}: {response.text}")
            return jsonify({
                "error": "ClipDrop API Error",
                "details": response.text
            }), 500

        # ---------------- SAVE IMAGE ----------------
        image_path = f"static/generated/{datetime.utcnow().timestamp()}.png"

        with open(image_path, "wb") as f:
            f.write(response.content)

        # Log saved image for debugging
        app.logger.info(f"Saved image: {image_path} for user: {email}")

        image_url = f"/{image_path}"
        # Build an absolute URL clients can use directly
        full_url = request.host_url.rstrip('/') + image_url
        app.logger.info(f"Image full URL: {full_url}")

        return jsonify({
            "status": "success",
            "image_url": image_url,
            "full_url": full_url
        }), 200

    except Exception as e:
        app.logger.exception("Error generating image")
        return jsonify({"error": str(e)}), 500

# Small endpoint to report server configuration (safe: doesn't expose secrets)
@app.route('/api/config', methods=['GET'])
def server_config():
    return jsonify({
        'ai_key_present': bool(bool(CLIPDROP_API_KEY)),
    }), 200

# Serve frontend index for convenience (so you can open http://localhost:5000)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # If the requested file exists relative to project root, serve it (useful for static assets),
    # otherwise serve index.html so SPA routes work.
    root = os.path.abspath(os.path.dirname(__file__))
    requested = os.path.join(root, path)
    if path and os.path.exists(requested):
        return send_from_directory(root, path)
    return send_from_directory(root, 'index.html')

# ---------------- RUN ----------------
if __name__ == "__main__":
    print(f"Starting Imaginify server on http://127.0.0.1:5000 — PID={os.getpid()}")
    if not CLIPDROP_API_KEY:
        print("WARNING: AI_API_KEY not set. Set it with $env:AI_API_KEY=\"your_key\" or create a .env file.")
    app.run(debug=True, host='127.0.0.1', port=5000)
