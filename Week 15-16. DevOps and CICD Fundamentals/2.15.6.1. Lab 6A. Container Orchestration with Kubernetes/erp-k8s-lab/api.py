from flask import Flask, jsonify
import math
import os

app = Flask(__name__)
# We will use this to demonstrate rolling updates
VERSION = os.environ.get("APP_VERSION", "v1.0")

@app.route('/health', methods=['GET'])
def health():
    # Kubernetes will constantly ping this. If it returns 500, K8s kills and restarts the pod.
    return jsonify({"status": "healthy"}), 200

@app.route('/api/workload', methods=['GET'])
def heavy_workload():
    # Simulating a heavy CPU task (e.g., generating a massive financial report)
    # This will spike the CPU and trigger our Kubernetes Auto-Scaler
    result = 0
    for i in range(1, 5000000):
        result += math.sqrt(i)
    return jsonify({"version": VERSION, "message": "Heavy workload completed!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
