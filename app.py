from flask import Flask, render_template, request, jsonify, send_from_directory
from sidekick import Sidekick
from langchain_core.messages import HumanMessage
import asyncio
import os
import traceback

app = Flask(__name__)
sidekick = Sidekick()

setup_complete = False  # track if setup is done

@app.before_request
def run_setup_once():
    """Ensure async sidekick.setup() only runs once."""
    global setup_complete
    if not setup_complete:
        asyncio.run(sidekick.setup())
        setup_complete = True

@app.after_request
def allow_iframe(response):
    """Allow embedding inside Shopify iframe."""
    response.headers["X-Frame-Options"] = "ALLOW-FROM https://ecomm-zilla.com"
    response.headers["Content-Security-Policy"] = "frame-ancestors https://ecomm-zilla.com"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Extract inputs
        user_input = request.form.get("message", "")
        criteria = request.form.get("criteria", "")
        history = []  # For now; can be extended to support session memory

        # Handle optional image upload
        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename:
                upload_dir = os.path.join(app.root_path, "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, image_file.filename)
                image_file.save(filepath)
                # You can pass filepath to Sidekick later if needed

        # Wrap message in expected format
        user_message = HumanMessage(content=user_input)
        result = asyncio.run(sidekick.run_superstep([user_message], criteria, history))

        return jsonify({"messages": result})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return "OK", 200

@app.route("/uploads/<path:filename>")
def uploads(filename):
    upload_dir = os.path.join(app.root_path, "uploads")
    return send_from_directory(upload_dir, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
