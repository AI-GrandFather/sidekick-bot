from flask import Flask, render_template, request, jsonify, send_from_directory
from sidekick import Sidekick
import asyncio
import os

app = Flask(__name__)
sidekick = Sidekick()

# Track setup completion
setup_complete = False

@app.before_request
def run_setup_once():
    """Ensure async sidekick.setup() only runs for the very first request."""
    global setup_complete
    if not setup_complete:
        asyncio.run(sidekick.setup())
        setup_complete = True

@app.after_request
def allow_iframe(response):
    """Allow embedding in Shopify store."""
    response.headers["X-Frame-Options"] = "ALLOW-FROM https://ecomm-zilla.com"
    response.headers["Content-Security-Policy"] = "frame-ancestors https://ecomm-zilla.com"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages (and optional image upload)."""
    try:
        message = request.form.get("message", "")
        criteria = request.form.get("criteria", "")
        history = []  # Extend if needed

        # Handle optional image upload
        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename:
                upload_dir = os.path.join(app.root_path, "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, image_file.filename)
                image_file.save(filepath)
                # Use `filepath` with sidekick if needed

        # Run the chat step
        result = asyncio.run(sidekick.run_superstep(message, criteria, history))
        return jsonify({"messages": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return "OK", 200

@app.route("/uploads/<path:filename>")
def uploads(filename):
    upload_dir = os.path.join(app.root_path, "uploads")
    return send_from_directory(upload_dir, filename)
