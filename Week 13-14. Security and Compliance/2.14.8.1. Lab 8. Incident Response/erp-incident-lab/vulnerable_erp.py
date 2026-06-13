from flask import Flask, request, jsonify
import logging
import time

app = Flask(__name__)

# We write logs to a file so we can perform forensics later
logging.basicConfig(filename='/app/erp_access.log', level=logging.INFO, 
                    format='%(asctime)s | IP: %(remote_addr)s | %(message)s')

# --- THE MISTAKE: A debug route left in production ---
@app.route('/api/debug/dump-customers', methods=['GET'])
def dump_customers():
    # Injecting the IP into the log record context
    ip = request.remote_addr
    
    # DETECTION: This log entry is our only clue a breach is happening!
    logging.critical(f"MASSIVE EXPORT TRIGGERED. 10,000 PII records accessed.", extra={'remote_addr': ip})
    
    return jsonify([
        {"name": "Juan Perez", "rfc": "PERJ850101HDF"}, 
        {"name": "Maria Lopez", "rfc": "LOMM900101XYZ"}
    ]), 200

@app.route('/api/health', methods=['GET'])
def health():
    logging.info("Health check ping.", extra={'remote_addr': request.remote_addr})
    return jsonify({"status": "online"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5080)

