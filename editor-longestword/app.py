from flask import Flask, request, jsonify, Response  # Imports Flask and JSON tools
from flask_cors import CORS  # Imports CORS to allow frontend requests
from time import time

# --- monitoring imports ---
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)  # Creates the Flask app instance
CORS(app)  # Enable CORS for all domains

# ---------------- monitoring setup ----------------
# give this service a name for the metrics
SERVICE_NAME = "longestword"

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
# Defines the route for the microservice
@app.route("/", methods=["GET"])
def longest_word():
    text = request.args.get("text", "")  # Gets the input text from the query string
    words_raw = text  # keep original for clarity

    # NEW: If no input (or only whitespace), return a clear error
    if not words_raw.strip():
        return jsonify({"error": "No input provided"}), 400

    words = words_raw.split()  # Splits the input into a list of words

    # If there are no words then it sets result to an empty string
    if not words:
        result = ""
    else:
        result = max(words, key=len)  # Finds the longest word using max()

    # Returns just the longest word
    return jsonify({
        "result": result
    })

# Runs the app on port 8083
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)

# Added this line to test git commits
