from flask import Flask, request, jsonify
from lxml import etree
import defusedxml.lxml as safe_etree
import sqlite3
import re
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize an in-memory database
db = sqlite3.connect(':memory:', check_same_thread=False)
db.execute("CREATE TABLE invoices (id INTEGER PRIMARY KEY, rfc TEXT, name TEXT)")
db.execute("INSERT INTO invoices (rfc, name) VALUES ('EKU9003173C9', 'Acme Corp')")
db.commit()


# ==========================================
#  VULNERABLE ENDPOINTS (DO NOT USE IN PROD)
# ==========================================

@app.route('/api/vulnerable/upload-cfdi', methods=['POST'])
def vulnerable_upload():
    """VULNERABILITY 1: XML External Entities (XXE)"""
    xml_data = request.data

    # The lxml parser is configured to resolve external entities (Highly Dangerous!)
    parser = etree.XMLParser(resolve_entities=True)

    try:

        root = etree.fromstring(xml_data, parser=parser)
        
        # We blindly trust the data extracted from the XML
        rfc = root.attrib.get('Rfc', 'UNKNOWN')
        name = root.attrib.get('Nombre', 'UNKNOWN')
        
        # VULNERABILITY 2: SQL Injection (String Concatenation)
        query = f"INSERT INTO invoices (rfc, name) VALUES ('{rfc}', '{name}')"
        db.execute(query)
        db.commit()
        
        # VULNERABILITY 3: Cross-Site Scripting (XSS) & Sensitive Data Exposure
        # We return the raw input back to the user without encoding it.
        return jsonify({"message": f"Invoice uploaded for {name} (RFC: {rfc})"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vulnerable/search', methods=['GET'])
def vulnerable_search():
    """VULNERABILITY 2: SQL Injection in Search"""
    rfc = request.args.get('rfc')
    
    # Blindly concatenating user input into the SQL query
    query = f"SELECT * FROM invoices WHERE rfc = '{rfc}'"
    cursor = db.execute(query)
    results = cursor.fetchall()

    return jsonify({"results": results}), 200

# ==========================================
#  SECURE ENDPOINTS (DEFENSE IN DEPTH)
# ==========================================

@app.route('/api/secure/upload-cfdi', methods=['POST'])
def secure_upload():
    xml_data = request.data
    try:
        # FIX 1: Prevent XXE. We use 'defusedxml' which actively blocks malicious entity expansion.
        root = safe_etree.fromstring(xml_data)
        rfc = root.attrib.get('Rfc', '')
        name = root.attrib.get('Nombre', '')
        
        # FIX 2: Server-Side Input Validation (Whitelist Approach)
        # Never trust the client. We enforce the strict Mexican RFC format using Regex.
        rfc_pattern = re.compile(r'^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$')
        if not rfc_pattern.match(rfc):
            # FIX 3: Insufficient Logging. We log the security anomaly!
            logging.warning(f"SECURITY ALERT: Rejected invalid RFC format: {rfc}")
            return jsonify({"error": "Invalid RFC format."}), 400
            
        # FIX 4: Prevent SQL Injection. We use Parameterized Queries (the ? syntax).
        # The database driver treats the input strictly as a string, never as executable code.
        db.execute("INSERT INTO invoices (rfc, name) VALUES (?, ?)", (rfc, name))
        db.commit()
        
        return jsonify({"message": "Invoice securely processed."}), 201

    except safe_etree.EntitiesForbidden:
        logging.critical("SECURITY ALERT: XXE Attack Detected and Blocked!")
        return jsonify({"error": "Malicious XML detected."}), 400
    except Exception as e:
        return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5040)

