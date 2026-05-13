import requests
import json
import sys

def process_order(sku, quantity, price_per_unit):
    print(f"--- Processing Order for {quantity}x {sku} ---")
    
    subtotal = quantity * price_per_unit
    
    # 1. Call the EXTERNAL API (SAT) to get official taxes
    print("1. Contacting External API (SAT) for tax calculation...")
    sat_payload = {"subtotal": subtotal}
    
    try:
        # Notice we route to the container name 'external-sat-api' on port 5000
        sat_response = requests.post("http://external-sat-api:5000/api/v1/calculate-tax", json=sat_payload)
        sat_response.raise_for_status() # Throws an error if we get a 400 or 500
        sat_data = sat_response.json()
        
        print(f"   Success! Official Total: ${sat_data['total_official']} (Stamp: {sat_data['sat_digital_stamp']})")
    except requests.exceptions.RequestException as e:
        print(f"   CRITICAL FAILURE: Could not reach SAT. Halting order. Error: {e}")
        sys.exit(1)

    # 2. Call the INTERNAL API (Inventory) to reserve the item
    print("2. Contacting Internal API (Inventory) to deduct stock...")
    inv_payload = {"sku": sku, "quantity": quantity}
    
    try:
        # Notice we route to the container name 'internal-inv-api' on port 5001
        inv_response = requests.post("http://internal-inv-api:5001/api/internal/inventory/deduct", json=inv_payload)
        
        if inv_response.status_code == 200:
            inv_data = inv_response.json()
            print(f"   Success! {inv_data['message']}. Remaining Stock: {inv_data['remaining_stock']}")
        else:
            # The API returned a clean error (like 400 Insufficient Stock), honoring the contract
            print(f"   ORDER FAILED: Inventory API returned error: {inv_response.json()['error']}")
    except requests.exceptions.RequestException as e:
        print(f"   CRITICAL FAILURE: Inventory service is down. Error: {e}")

if __name__ == '__main__':
    # Test a successful order
    process_order("WIDGET-01", 5, 200.00)
    print("\n")
    # Test an order that fails the Internal API rules (Asking for 100 items when we only have 45 left)
    process_order("WIDGET-01", 100, 200.00)
