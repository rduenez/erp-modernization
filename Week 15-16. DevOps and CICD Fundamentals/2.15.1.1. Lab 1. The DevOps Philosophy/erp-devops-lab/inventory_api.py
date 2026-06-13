from flask import Flask, jsonify
import time

app = Flask(__name__)
start_time = time.time()

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    return jsonify({"status": "success", "items": 150}), 200

# DevOps Principle: Monitoring & Feedback Loops
@app.route('/health', methods=['GET'])
def health_check():
    uptime = round(time.time() - start_time, 2)
    return jsonify({"status": "healthy", "uptime_seconds": uptime}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
