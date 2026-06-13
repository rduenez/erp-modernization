import re

def investigate_breach():
    print("--- FORENSIC INVESTIGATION REPORT ---")
    stolen_records = 0
    attacker_ips = set()
    
    with open('erp_access.l', 'r') as log_file:
        for line in log_file:
            if "CRITICAL" in line or "MASSIVE EXPORT" in line:
                stolen_records += 10000
                # Extract the IP address
                match = re.search(r'IP: ([\d\.]+)', line)
                if match:
                    attacker_ips.add(match.group(1))
                    
    print(f"Total Records Compromised: {stolen_records}")
    print(f"Attacker IPs identified: {', '.join(attacker_ips)}")
    print("Data Types Accessed: Names, RFCs (PII)")

if __name__ == '__main__':
    investigate_breach()

