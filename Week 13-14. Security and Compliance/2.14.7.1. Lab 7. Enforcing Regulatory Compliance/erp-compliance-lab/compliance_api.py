from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timezone
import base64

app = Flask(__name__)
# --- COMPLIANCE STORAGE ---
# 1. SOX Immutable Audit Trail (Append-Only Log)
audit_log = []
# 2. 5-Year SAT Retention Database
invoices_db = {}
# 3. COFEPRIS Regulated Inventory
pharma_inventory = []


def log_audit(action, user, details):
    """SOX Requirement: Immutable record of who did what, and when."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user,
        "action": action,
        "details": details
    }
    audit_log.append(entry)
    print(f"[AUDIT] {entry['timestamp']} | User: {user} | Action: {action}")


# Load the mock SAT Private Key
def load_private_key():
    with open("mock_fiel.key", "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)


# --- 1. SAT COMPLIANCE: CFDI 4.0 SIGNING ---
@app.route('/api/compliance/invoice', methods=['POST'])
def generate_invoice():
    data = request.get_json()
    user_id = request.headers.get('X-User-Id', 'UNKNOWN')


    # 1. Prepare the payload string (Simulating the SAT Cadena Original)
    cadena_original = f"||4.0|{data['rfc']}|{data['amount']}||"
    # 2. Cryptographically sign the payload using the private key (Sello Digital)
    private_key = load_private_key()
    signature = private_key.sign(
        cadena_original.encode('utf-8'),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    sello_digital = base64.b64encode(signature).decode('utf-8')
    print(sello_digital)
    
    invoice_record = {
        "cadena_original": cadena_original,
        "sello_digital": sello_digital,
        "retention_expires": (datetime.now(timezone.utc).replace(year=datetime.now().year + 5)).isoformat()
    }
    invoices_db[data['invoice_id']] = invoice_record
    
    # 3. Log the action for SOX auditors
    log_audit("GENERATE_CFDI", user_id, f"Invoice {data['invoice_id']} signed for {data['rfc']}")
    
    return jsonify({"message": "Invoice signed successfully.", "cfdi_data": invoice_record}), 201


# --- 2. COFEPRIS COMPLIANCE: REGULATED INVENTORY ---
@app.route('/api/compliance/pharma-inventory', methods=['POST'])
def add_pharma_inventory():
    data = request.get_json()
    user_id = request.headers.get('X-User-Id', 'UNKNOWN')
    
    # STRICT ENFORCEMENT: Reject if missing regulatory tracking data
    if not data.get('lote') or not data.get('fecha_caducidad'):
        log_audit("FAILED_INVENTORY_ADD", user_id, "Rejected: Missing COFEPRIS Lot/Expiration data.")
        return jsonify({"error": "COFEPRIS Compliance Failure: Batch/Lot and Expiration Date are legally required."}), 400
        
    pharma_inventory.append(data)
    log_audit("ADD_PHARMA_INVENTORY", user_id, f"Added Batch {data['lote']} of {data['medicamento']}")
    
    return jsonify({"message": "Inventory added in compliance with regulations."}), 201


# --- 3. SOX COMPLIANCE: AUDIT REPORTING ---
@app.route('/api/compliance/audit-report', methods=['GET'])
def get_audit_report():
    user_id = request.headers.get('X-User-Id', 'UNKNOWN')
    
    # Normally, you would restrict this endpoint via RBAC to only 'ComplianceOfficers'
    log_audit("VIEW_AUDIT_TRAIL", user_id, "Requested complete compliance audit log")
    return jsonify({"sox_audit_trail": audit_log}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5070)

