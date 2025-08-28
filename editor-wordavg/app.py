from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import re
from time import time

# --- monitoring imports ---
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Create the Flask app instance
app = Flask(__name__)
# Allow CORS for frontend access
CORS(app)

# ---------------- monitoring setup ----------------
# give this service a name for the metrics
SERVICE_NAME = "avgword"

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
# Define route for GET requests
@app.route("/", methods=["GET"])
def avg_word_length():
    text = request.args.get("text", "")
    # Use regex to remove punctuation
    clean_text = re.sub(r'[^\w\s]', '', text)
    words = clean_text.split()
    total_letters = sum(len(word) for word in words)
    total_words = len(words)

    if total_words == 0:
        avg = 0
    else:
        avg = round(total_letters / total_words, 2)

    # Return just the number as a string in 'description' field
    return jsonify({
        "result": avg,
        "description": str(avg)
    })

# Start the server on all interfaces, port 8081
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
