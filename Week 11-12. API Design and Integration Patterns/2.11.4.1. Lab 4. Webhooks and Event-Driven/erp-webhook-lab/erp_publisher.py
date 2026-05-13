import requests
import json
import hmac
import hashlib
import time

WEBHOOK_SECRET = b"super_secret_logistics_key_2026"
# Pointing to the container name on our Podman network
WEBHOOK_URL = "http://shipping-api:5005/webhook/order-ready"

def send_webhook_with_retry(payload, max_retries=3):
    # Convert payload to a JSON string and encode it to bytes for hashing
    payload_bytes = json.dumps(payload).encode('utf-8')
    
    # SECURITY: Generate the HMAC-SHA256 signature
    signature = hmac.new(WEBHOOK_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-ERP-Signature': f"sha256={signature}"
    }

    # RETRY LOGIC: What if the receiving system is down?
    attempt = 1
    while attempt <= max_retries:
        print(f"Attempt {attempt}: Sending Webhook to Shipping System...")
        try:
            response = requests.post(WEBHOOK_URL, data=payload_bytes, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("Webhook delivered successfully!")
                return True
            else:
                print(f"Shipping system rejected the payload. Status: {response.status_code}")
                break # We don't retry 400 errors (Bad Request), only network failures/500s
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            
        print(f"Failed to deliver. Waiting 3 seconds before retry...")
        time.sleep(3)
        attempt += 1

    print("CRITICAL: Webhook delivery failed permanently after max retries.")
    return False

if __name__ == '__main__':
    # The Event: A new order was just confirmed
    new_order_event = {
        "event_type": "order.confirmed",
        "order_id": "ORD-2026-5541",
        "shipping_address": "Av. Guerrero 123, Irapuato, GTO",
        "items": ["Industrial Widget x2"]
    }
    
    print("--- 1. Testing Normal Delivery ---")
    send_webhook_with_retry(new_order_event)


