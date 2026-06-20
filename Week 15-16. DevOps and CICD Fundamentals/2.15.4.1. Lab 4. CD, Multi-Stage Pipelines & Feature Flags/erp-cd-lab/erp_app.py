from flask import Flask, jsonify
import os

app = Flask(__name__)

# FEATURE FLAG: Toggle this via environment variables
NEW_PAYMENT_GATEWAY_ENABLED = os.environ.get("ENABLE_NEW_PAYMENT_GATEWAY", "false").lower() == "true"

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if NEW_PAYMENT_GATEWAY_ENABLED:
        # The new, unreleased code path
        return jsonify({"message": "Payment processed using the NEW V2 Gateway!"}), 200
    else:
        # The legacy code path
        return jsonify({"message": "Payment processed using the legacy V1 Gateway."}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
