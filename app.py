from flask import Flask, render_template, request, jsonify, send_from_directory
from sidekick import Sidekick
from langchain_core.messages import HumanMessage
import asyncio
import os
import traceback

# Initialize Flask app
app = Flask(__name__)

# Initialize Sidekick instance
sidekick = Sidekick()
setup_complete = False

# ---------------------------------------------
# Run async setup once before handling requests
# ---------------------------------------------
@app.before_request
def run_setup_once():
    global setup_complete
    if not setup_complete:
        asyncio.run(sidekick.setup())
        setup_complete = True

# ----------------------------------------------------
# Allow iframe embedding for Shopify (frame-ancestor)
# ----------------------------------------------------
@app.after_request
def allow_iframe(response):
    response.headers["X-Frame-Options"] = "ALLOW-FROM https://ecomm-zilla.com"
    response.headers["Content-Security-Policy"] = "frame-ancestors https://ecomm-zilla.com"
    return response

# -------------------
#   ROUTE: Home Page
# -------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------
#   ROUTE: Chat API
# -------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        message = request.form.get("message", "")
        criteria = request.form.get("criteria", "")
        history = []

        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename:
                upload_dir = os.path.join(app.root_path, "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, image_file.filename)
                image_file.save(filepath)

        user_message = {"role": "user", "content": message}

        # Reuse the Sidekick's dedicated event loop
        result = sidekick.loop.run_until_complete(
            sidekick.run_superstep([user_message], criteria, history)
        )

        # Convert LangChain messages to JSON-safe output
        json_ready_result = [
            {"role": m["role"], "content": m["content"]} for m in result
        ]
        return jsonify({"messages": json_ready_result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -------------------
#   ROUTE: Healthcheck
# -------------------
@app.route("/health")
def health():
    return "OK", 200

# -------------------
#   ROUTE: Serve Uploaded Files (Optional)
# -------------------
@app.route("/uploads/<path:filename>")
def uploads(filename):
    upload_dir = os.path.join(app.root_path, "uploads")
    return send_from_directory(upload_dir, filename)

# -------------------
#   Entry Point
# -------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
