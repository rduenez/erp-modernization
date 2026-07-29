from flask import Flask, request, jsonify
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Histogram, generate_latest
import logging
import time
import sys
import random

app = Flask(__name__)

# --- 1. STRUCTURED LOGGING SETUP ---
# We configure Python to output logs as JSON instead of plain text.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(module)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# --- 2. APM METRICS SETUP ---
# Track HTTP request counts by method and endpoint
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'http_status'])
# Track response times (latency)
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'Request latency', ['endpoint'])

# Middleware to track APM metrics automatically on every request
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, http_status=response.status_code).inc()
    return response

# --- 3. BUSINESS & SECURITY ENDPOINTS ---
@app.route('/api/invoice', methods=['POST'])
def process_invoice():
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # BUSINESS EVENT LOGGING (INFO Level)
    logger.info("Invoice processed successfully", extra={"action": "invoice_processed", "amount": 1500, "currency": "MXN"})
    return jsonify({"status": "processed"}), 200

@app.route('/api/login', methods=['POST'])
def secure_login():
    user = request.get_json().get('user')
    # SECURITY EVENT LOGGING (WARN Level for failed attempts)
    logger.warning("Failed login attempt detected", extra={"action": "security_alert", "user": user, "ip": request.remote_addr})
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/api/crash', methods=['GET'])
def trigger_crash():
    # APPLICATION ERROR LOGGING (ERROR/FATAL Level)
    logger.error("Database connection timeout", extra={"action": "db_error", "db_host": "db.internal"})
    return jsonify({"error": "Internal Server Error"}), 500

# --- 4. EXPOSE METRICS FOR SCRAPING ---
@app.route('/metrics', methods=['GET'])
def metrics():
    # This endpoint is polled by APM tools like Prometheus or Datadog
    return generate_latest(), 200

if __name__ == '__main__':
    logger.info("Starting ERP API", extra={"version": "1.0.0", "environment": "production"})
    app.run(host='0.0.0.0', port=8080)
