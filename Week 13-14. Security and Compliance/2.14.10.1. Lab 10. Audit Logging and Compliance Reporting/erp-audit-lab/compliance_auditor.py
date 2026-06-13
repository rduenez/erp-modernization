import json
import hashlib
LOG_FILE = "secure_audit.jsonl"

def verify_and_report():
    print("=== INITIATING COMPLIANCE AUDIT & INTEGRITY CHECK ===\n")
    
    expected_prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    line_number = 1
    tampered = False
    
    report_data = {
        "logins": 0,
        "admin_actions": [],
        "financial_changes": []
    }
    
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                record = json.loads(line)
                
                # 1. Extract the saved signature and temporarily remove it to recalculate
                saved_signature = record.pop("signature")

                # 2. Check the cryptographic chain
                if record["prev_hash"] != expected_prev_hash:
                    print(f"CRITICAL TAMPER DETECTED at Line {line_number}!")
                    print(f"Chain broken. Expected Prev Hash: {expected_prev_hash[:8]}..., Found: {record['prev_hash'][:8]}...")
                    tampered = True
                    break
                
                # 3. Recalculate the current hash
                payload_str = json.dumps(record, sort_keys=True)
                recalculated_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
                
                if recalculated_hash != saved_signature:
                    print(f"CRITICAL TAMPER DETECTED at Line {line_number}!")
                    print(f"Payload was altered! Saved Signature: {saved_signature[:8]}... Recalculated: {recalculated_hash[:8]}...")
                    tampered = True
                    break
                
                # Chain is valid, update expected hash for next loop
                expected_prev_hash = saved_signature
                
                # --- GATHER COMPLIANCE REPORTING DATA ---
                if record['event_type'] == "SYSTEM_ACCESS":
                    report_data["logins"] += 1
                elif record['event_type'] == "ADMIN_ACTION":
                    report_data["admin_actions"].append(f"{record['actor']} changed {record['target_id']}: {record['data_before']['role']} -> {record['data_after']['role']}")
                elif record['event_type'] == "DATA_CHANGE":
                    report_data["financial_changes"].append(f"{record['actor']} modified {record['target_id']} salary: {record['data_before']['salary']} -> {record['data_after']['salary']}")
                
                line_number += 1

    except FileNotFoundError:
        print("Audit log missing!")
        return

    if not tampered:
        print("INTEGRITY CHECK PASSED: Cryptographic chain is mathematically sound. 0 tampering detected.\n")
        print("=== QUARTERLY COMPLIANCE & ACCESS REPORT ===")
        print(f"Total Login Attempts: {report_data['logins']}")
        print("\n[Administrative Permission Changes]:")
        for act in report_data["admin_actions"]:
            print(f" - {act}")
        print("\n[Financial Data Modifications]:")
        for fin in report_data["financial_changes"]:
            print(f" - {fin}")
        print("\n[CONCLUSION]: Ready for external ISO 27001 / SOX auditor review.")

if __name__ == '__main__':
    verify_and_report()

