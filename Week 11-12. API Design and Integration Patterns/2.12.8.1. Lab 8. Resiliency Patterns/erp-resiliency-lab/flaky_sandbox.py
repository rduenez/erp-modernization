import time
import random
from flask import Flask, jsonify

app = Flask(__name__)

# State variable to simulate a total outage
system_crashed = False

@app.route('/api/v1/credit-score', methods=['GET'])
def get_credit_score():
    global system_crashed
    
    if system_crashed:
        return jsonify({"error": "Service Unavailable"}), 503

    chance = random.random()
    
    # 30% chance to throw a temporary internal server error
    if chance < 0.30:
        return jsonify({"error": "Internal Server Error"}), 500
           
    # 20% chance to simulate severe lag (SLA Breach!)
    elif chance < 0.50:
        time.sleep(3)
        return jsonify({"status": "success", "score": 750}), 200
        
    # 50% chance to work perfectly
    else:
        return jsonify({"status": "success", "score": 720}), 200

@app.route('/api/v1/crash-system', methods=['POST'])
def crash():
    """Admin endpoint to intentionally crash the sandbox"""
    global system_crashed
    system_crashed = True
    return jsonify({"message": "Sandbox API has been crashed!"}), 200

@app.route('/api/v1/restore', methods=['POST'])
def restore():
    """Admin endpoint to intentionally recover the sandbox"""
    global system_crashed
    system_crashed = False
    return jsonify({"message": "Sandbox API has recovered!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012)
