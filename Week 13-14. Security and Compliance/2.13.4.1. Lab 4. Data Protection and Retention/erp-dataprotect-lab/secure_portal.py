from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
import re
import uuid

app = Flask(__name__)

# --- SECRETS & ENCRYPTION SETUP ---
MASTER_ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(MASTER_ENCRYPTION_KEY)

# Mock Databases
customer_db = {}
payment_vault = {}
cold_storage_archive = {} # Simulating secure, long-term archival storage (e.g., S3 Glacier)


# --- HELPER FUNCTIONS ---
def mask_pan(pan):
    """PCI-DSS: Only display the last 4 digits of a credit card."""
    pan_clean = re.sub(r'\D', '', pan)
    return f"****-****-****-{pan_clean[-4:]}"


# --- 1. LFPDPPP: SECURE PII STORAGE & PRIVACY NOTICE ---
@app.route('/api/v1/customer', methods=['POST'])
def save_customer():

    data = request.get_json()

    # LFPDPPP Check: Did they accept the Privacy Notice (Aviso de Privacidad)?
    if not data.get('accepted_privacy_notice'):
        return jsonify({"error": "Consent for data collection is required by law."}), 400
        
    customer_id = str(uuid.uuid4())
    
    # Encrypt highly sensitive PII BEFORE it touches the database
    rfc_encrypted = cipher_suite.encrypt(data['rfc'].encode('utf-8'))
    address_encrypted = cipher_suite.encrypt(data['address'].encode('utf-8'))
    
    customer_db[customer_id] = {
        "name": data['name'], 
        "rfc_secure": rfc_encrypted,
        "address_secure": address_encrypted,
        "created_at": datetime.now(timezone.utc)
    }
    
    return jsonify({"message": "Customer saved securely.", "id": customer_id}), 201


# --- 2. LFPDPPP: ARCO RIGHTS (Derecho de Cancelación) ---
@app.route('/api/v1/customer/<customer_id>/arco-cancel', methods=['DELETE'])
def exercise_arco_rights(customer_id):
    """
    By Mexican law, users can demand their PII be deleted.
    We must physically and permanently remove it from active systems.
    """
    if customer_id in customer_db:
        # SECURE DELETION: We do not just mark 'active=false' (Soft Delete).
        # We physically remove the PII from the dictionary/memory.
        del customer_db[customer_id]
        return jsonify({"message": "ARCO Rights honored. Personal data securely and permanently erased."}), 200
    
    return jsonify({"error": "Customer not found."}), 404


# --- 3. PCI-DSS: PAYMENT PROCESSING & TOKENIZATION ---
@app.route('/api/v1/checkout', methods=['POST'])
def process_payment():

    data = request.get_json()
    pan = data.get('pan')
    cvv = data.get('cvv')
    
    if not pan or not cvv:
        return jsonify({"error": "Missing payment details"}), 400
        
    # PCI-DSS REQUIREMENT: The CVV is used to authorize the transaction with the bank...
    print(f"[BANKING] Authorizing charge using CVV: {cvv}...")

    # ...but it MUST be immediately discarded. Never log it, never save it.
    cvv = None

    # Tokenization: Save a secure reference to the card, not the card itself
    payment_token = f"tok_{uuid.uuid4().hex[:10]}"
    masked_card = mask_pan(pan)
    
    # For this lab, we inject a fake 'created_at' date 5.1 years ago to test our retention script
    old_date = datetime.now(timezone.utc) - timedelta(days=1865)
    
    payment_vault[payment_token] = {
        "card_network": "Visa",
        "masked_pan": masked_card,
        "amount_mxn": data.get('amount'),
        "transaction_date": old_date # Simulating a very old transaction
    }
    
    return jsonify({
        "message": "Payment successful",
        "payment_token": payment_token,
        "saved_card": masked_card
    }), 200


# --- 4. DATA RETENTION & DISPOSAL ENGINE ---
@app.route('/api/v1/admin/run-retention-job', methods=['POST'])
def run_retention_job():
    """
    Mexican CFF requires 5 years of accounting record retention.
    This job sweeps the active database, moves 5-year-old records to cold storage,
    and securely deletes them from the active, expensive database.
    """
    print("\n--- RUNNING DATA RETENTION SWEEP (5-YEAR RULE) ---")
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1825) # 5 years
    archived_count = 0
    keys_to_delete = []  
    for token, record in payment_vault.items():
        if record['transaction_date'] < cutoff_date:
            print(f"Archiving old transaction {token} from {record['transaction_date'].strftime('%Y-%m-%d')}...")
            
            # 1. Archival: Move to Secure Cold Storage
            cold_storage_archive[token] = record
            
            # 2. Secure Deletion Prep
            keys_to_delete.append(token)
            archived_count += 1
            
    # 3. Secure Deletion: Physically wipe from active database
    for key in keys_to_delete:
        del payment_vault[key]
        
    return jsonify({
        "message": "Retention job complete", 
        "archived_records": archived_count,
        "active_records_remaining": len(payment_vault)
    }), 200


if __name__ == '__main__':
    # ENCRYPTION IN TRANSIT: We enforce HTTPS using a self-signed adhoc certificate
    print("Starting secure server on HTTPS...")
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')

