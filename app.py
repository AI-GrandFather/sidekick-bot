from flask import Flask, render_template, request, jsonify, send_from_directory
from sidekick import Sidekick
import asyncio
import os

app = Flask(__name__)
sidekick = Sidekick()

# ---------------------------------------------------------------------------
# Initialise Sidekick **once** when the first HTTP request comes in (Flask ≥3)
# ---------------------------------------------------------------------------
setup_complete = False

@app.before_request
def run_setup_once():
    """Ensure async sidekick.setup() only runs for the very first request."""
    global setup_complete
    if not setup_complete:
        asyncio.run(sidekick.setup())
        setup_complete = True

# -------------------
#   ROUTE: Home page
# -------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------
#   ROUTE: Chat API
# -------------------
@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages (and optional image upload)."""
    try:
        # Text fields
        message = request.form.get("message", "")
        criteria = request.form.get("criteria", "")
        history = []  # Placeholder – extend to real history if needed

        # Handle optional image upload (not yet used by the agent)
        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename:
                upload_dir = os.path.join(app.root_path, "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, image_file.filename)
                image_file.save(filepath)
                # You could pass the path to sidekick here if desired

        # Run Sidekick graph step
        result = asyncio.run(sidekick.run_superstep(message, criteria, history))
        return jsonify({"messages": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------
#   ROUTE: Healthcheck
# -------------------
@app.route("/health")
def health():
    return "OK", 200

# -------------------
#   ROUTE: serve uploads (optional)
# -------------------
@app.route("/uploads/<path:filename>")
def uploads(filename):
    """Serve uploaded files back to the browser if needed."""
    upload_dir = os.path.join(app.root_path, "uploads")
    return send_from_directory(upload_dir, filename)

# -------------------
#   Main entrypoint
# -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
