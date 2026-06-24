from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

# Fetch configurations from the Environment
# If a critical secret is missing, the application should crash immediately (Fail Fast)
DB_CONN = os.environ.get("DB_CONNECTION")
PAYMENT_KEY = os.environ.get("PAYMENT_API_KEY")
SAT_KEY = os.environ.get("SAT_API_KEY")

if not all([DB_CONN, PAYMENT_KEY, SAT_KEY]):
    print("CRITICAL ERROR: Missing required configuration variables. Shutting down.")
    sys.exit(1)

# Feature Flags have safe defaults (e.g., False if not explicitly enabled)
NEW_UI_ENABLED = os.environ.get("ENABLE_NEW_UI", "false").lower() == "true"

@app.route('/api/system-info', methods=['GET'])
def system_info():
    # Masking secrets for the output so we don't expose them in the browser
    masked_payment = f"***{PAYMENT_KEY[-4:]}" if PAYMENT_KEY else "None"
    
    return jsonify({
        "database_target": DB_CONN.split('@')[1] if '@' in DB_CONN else "Unknown",
        "payment_gateway_status": f"Connected (Key: {masked_payment})",
        "new_ui_active": NEW_UI_ENABLED
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

