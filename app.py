import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", "")

# Use the correct per-model endpoint — no "model" field, no "version" field needed
REPLICATE_MODEL_ENDPOINTS = {
    "480p": "https://api.replicate.com/v1/models/wavespeedai/wan-2.1-t2v-480p/predictions",
    "720p": "https://api.replicate.com/v1/models/wavespeedai/wan-2.1-t2v-720p/predictions",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Start a prediction and immediately return the prediction ID.
    The frontend polls /status/<id> until done — no long blocking request."""

    data = request.json
    prompt = data.get("prompt", "").strip()
    resolution = data.get("resolution", "480p")
    steps = int(data.get("steps", 30))
    style = data.get("style", "")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if not REPLICATE_API_KEY:
        return jsonify({"error": "REPLICATE_API_KEY is not set. Add it in Render → Environment."}), 500

    full_prompt = prompt + style
    endpoint = REPLICATE_MODEL_ENDPOINTS.get(resolution, REPLICATE_MODEL_ENDPOINTS["480p"])

    headers = {
        "Authorization": f"Bearer {REPLICATE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "respond-async",   # tell Replicate not to wait
    }

    payload = {
        "input": {
            "prompt": full_prompt,
            "num_inference_steps": steps,
            "guidance_scale": 5,
            "fast_mode": "Fast",
        }
    }

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=20)
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to Replicate timed out. Please try again."}), 504

    if not resp.ok:
        try:
            detail = resp.json().get("detail", f"API error {resp.status_code}: {resp.text[:200]}")
        except Exception:
            detail = f"API error {resp.status_code}"
        return jsonify({"error": detail}), resp.status_code

    prediction = resp.json()
    return jsonify({"prediction_id": prediction["id"]}), 200


@app.route("/status/<prediction_id>", methods=["GET"])
def status(prediction_id):
    """Called every 3s by the frontend to check if the video is ready."""

    if not REPLICATE_API_KEY:
        return jsonify({"error": "REPLICATE_API_KEY is not set."}), 500

    headers = {"Authorization": f"Bearer {REPLICATE_API_KEY}"}

    try:
        resp = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers=headers,
            timeout=15,
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": "Status check timed out"}), 504

    if not resp.ok:
        return jsonify({"error": f"Status check failed: {resp.status_code}"}), resp.status_code

    data = resp.json()
    result_status = data.get("status")

    if result_status == "succeeded":
        output = data.get("output")
        video_url = output[0] if isinstance(output, list) else output
        return jsonify({"status": "succeeded", "video_url": video_url})

    elif result_status in ("failed", "canceled"):
        return jsonify({
            "status": result_status,
            "error": data.get("error", "Generation failed. Please try again.")
        }), 500

    # still queued / processing — frontend keeps polling
    return jsonify({"status": result_status})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
