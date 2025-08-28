from flask import Flask, request, jsonify, Response   # Response needed for /metrics
from flask_cors import CORS
import string
from time import time

# --- monitoring imports ---
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

# ---------------- monitoring setup ----------------
# give this service a name for the metrics
SERVICE_NAME = "puncount"

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
# endpoint that counts punctuation in a string
@app.route("/", methods=["GET"])
def count_punctuation():
    # get the text from the query string
    text = request.args.get("text", "")
    punctuations = list(string.punctuation)
    
    # count how many characters in the text are punctuation marks
    punctuation_count = sum(1 for char in text if char in punctuations)

    # send back result + a description message
    return jsonify({
        "result": punctuation_count,
        "description": f"{punctuation_count} punctuation characters found"
    })

# run the service on port 8082 (not 80) so it matches frontend + proxy
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
