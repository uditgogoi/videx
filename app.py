import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
MODEL = "wavespeedai/wan-2.1-t2v-480p"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt", "").strip()
    steps = data.get("steps", 30)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if not REPLICATE_API_TOKEN:
        return jsonify({"error": "REPLICATE_API_TOKEN not set on server"}), 500

    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "num_inference_steps": steps,
            "guidance_scale": 5,
            "fast_mode": "Fast"
        }
    }

    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    resp = requests.post(REPLICATE_API_URL, json=payload, headers=headers)

    if not resp.ok:
        return jsonify({"error": resp.json().get("detail", "Failed to create prediction")}), resp.status_code

    return jsonify(resp.json())


@app.route("/api/status/<prediction_id>", methods=["GET"])
def status(prediction_id):
    if not REPLICATE_API_TOKEN:
        return jsonify({"error": "REPLICATE_API_TOKEN not set on server"}), 500

    headers = {"Authorization": f"Bearer {REPLICATE_API_TOKEN}"}
    resp = requests.get(f"{REPLICATE_API_URL}/{prediction_id}", headers=headers)

    if not resp.ok:
        return jsonify({"error": "Failed to fetch status"}), resp.status_code

    return jsonify(resp.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
