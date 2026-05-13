from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

# This is the shared secret key. In production, this lives in environment variables!
WEBHOOK_SECRET = b"super_secret_logistics_key_2026"

def verify_signature(payload_body, signature_header):
    """Hashes the incoming payload with the secret key and compares it to the header"""
    if not signature_header:
        return False
        
    expected_hmac = hmac.new(WEBHOOK_SECRET, payload_body, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={expected_hmac}"
    
    # hmac.compare_digest prevents timing attacks
    return hmac.compare_digest(expected_signature, signature_header)


@app.route('/webhook/order-ready', methods=['POST'])
def receive_order_webhook():
    # 1. Get the raw payload and the signature from the headers
    raw_payload = request.get_data()
    signature_header = request.headers.get('X-ERP-Signature')
    
    # 2. SECURITY: Validate the Webhook
    if not verify_signature(raw_payload, signature_header):
        print("SECURITY ALERT: Invalid webhook signature detected. Dropping request.")
        return jsonify({"error": "Unauthorized. Bad Signature."}), 401
        
    # 3. Process the Event
    data = request.get_json()
    order_id = data.get('order_id')
    destination = data.get('shipping_address')
    
    print(f"WEBHOOK RECEIVED: Order {order_id} is ready to ship to {destination}!")
    
    # 4. Acknowledge Receipt quickly (always return 200 OK so the publisher knows you got it)
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)

