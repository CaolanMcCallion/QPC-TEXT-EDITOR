from flask import Flask, request, jsonify, Response   # Imports Flask and JSON tools
from flask_cors import CORS  # Imports CORS to allow frontend requests
from time import time

# --- monitoring imports ---
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Create Flask app 
app = Flask(__name__)
# Enables CORS to allow frontend requests from other places
CORS(app)

# ---------------- monitoring setup ----------------
# give this service a name for the metrics
SERVICE_NAME = "vowelcount"

# counter that tracks all requests (split by service, method, endpoint, status code)
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status"]
)

# histogram that tracks how long requests take (latency)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["service", "endpoint"]
)

# start a timer before every request
@app.before_request
def _start_timer():
    request._t0 = time()

# after the request finishes, record latency + count
@app.after_request
def _record_metrics(resp):
    try:
        dt = time() - getattr(request, "_t0", time())
        REQUEST_LATENCY.labels(SERVICE_NAME, request.path).observe(dt)
        REQUEST_COUNT.labels(SERVICE_NAME, request.method, request.path, resp.status_code).inc()
    finally:
        return resp

# simple health check so we can see if service is alive
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# prometheus scrape endpoint
@app.route("/metrics", methods=["GET"])
def metrics():
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

# ---------------- actual service logic ----------------
# Define the main GET endpoint for counting vowels
@app.route("/", methods=["GET"])
def count_vowels():
    # Get the 'text' query param from the request
    text = request.args.get("text", "")

    # Error handling if no input text provided (after stripping whitespace)
    if not text.strip():
        return jsonify({"error": "No input provided"}), 400

    # Count the number of vowels in the input string
    count = sum(1 for c in text.lower() if c in "aeiou")

    # Returns the result in JSON 
    return jsonify({
        "result": count,
        "description": f"{count} vowels found"
    })

# Run the Flask app on port 8080
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
