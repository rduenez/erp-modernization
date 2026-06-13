from flask import Flask, request, jsonify
from datetime import datetime, timezone
import hashlib
import json
import os

app = Flask(__name__)

# --- IN-MEMORY DATABASE ---
db = {
    "EMP_101": {"name": "Alice", "salary": 80000, "role": "Employee"},
    "EMP_102": {"name": "Bob", "salary": 95000, "role": "Admin"}
}

# --- THE TAMPER-PROOF LOGGER ---
LOG_FILE = "secure_audit.jsonl"
last_hash = "0000000000000000000000000000000000000000000000000000000000000000" # Genesis hash

def write_audit_log(event_type, actor, target_id, details, before=None, after=None):

    global last_hash

    # 1. Construct the payload
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor_ip": request.remote_addr,
        "actor": actor,
        "target_id": target_id,
        "details": details,
        "data_before": before,
        "data_after": after,
        "prev_hash": last_hash
    }
    
    # 2. Cryptographically seal the payload
    # Convert dict to a deterministic JSON string to ensure consistent hashing
    payload_str = json.dumps(payload, sort_keys=True)
    new_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    # 3. Add the signature and write to disk
    payload["signature"] = new_hash
    last_hash = new_hash
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(payload) + "\n")
        
    print(f"[AUDIT LOGGED] {event_type} by {actor} | Signature: {new_hash[:8]}...")


# --- ERP ENDPOINTS ---
@app.route('/api/login', methods=['POST'])
def login():
    """System Access Logging"""
    data = request.get_json()
    user = data.get('username')
    
    # Simulate login validation
    status = "SUCCESS" if user in ["Alice", "Bob"] else "FAILED"
    
    write_audit_log(
        event_type="SYSTEM_ACCESS", 
        actor=user, 
        target_id=user, 
        details=f"Login attempt {status}"
    )
    return jsonify({"message": f"Login {status}"}), 200


@app.route('/api/employee/<emp_id>/salary', methods=['PUT'])
def update_salary(emp_id):
    """Data Changes Logging (Before/After values)"""
    actor = request.headers.get('X-User-Id')
    new_salary = request.get_json().get('salary')
    
    old_data = db[emp_id].copy()
    db[emp_id]['salary'] = new_salary
    new_data = db[emp_id].copy()
    
    write_audit_log(
        event_type="DATA_CHANGE", 
        actor=actor, 
        target_id=emp_id, 
        details="Salary modification",
        before=old_data,
        after=new_data
    )
    return jsonify({"message": "Salary updated"}), 200

@app.route('/api/employee/<emp_id>/role', methods=['PUT'])
def change_role(emp_id):
    """Administrative Actions Logging"""
    actor = request.headers.get('X-User-Id')
    new_role = request.get_json().get('role')
    
    old_data = db[emp_id].copy()
    db[emp_id]['role'] = new_role
    new_data = db[emp_id].copy()
    
    write_audit_log(
        event_type="ADMIN_ACTION", 
        actor=actor, 
        target_id=emp_id, 
        details="Role/Permission escalated",
        before=old_data,
        after=new_data
    )
    return jsonify({"message": "Role updated"}), 200

if __name__ == '__main__':
    # Initialize the log file
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    app.run(host='0.0.0.0', port=5100)
