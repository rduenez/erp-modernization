from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
VERSION = "1.1.0" # MINOR bump: New feature, backwards compatible

# ROLLBACK STRATEGY: Feature Flags
# If the new tax engine causes bugs, we can turn it off via env var without redeploying code.
ENABLE_NEW_TAX_ENGINE = os.environ.get("ENABLE_NEW_TAX_ENGINE", "false").lower() == "true"

def init_db():
    conn = sqlite3.connect('billing.db')
    conn.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY, amount REAL)")
    
    # SAFE MIGRATION: Adding a column is backward compatible. 
    # v1.0.0 code will just ignore this column if we have to rollback.

    try:
        conn.execute("ALTER TABLE invoices ADD COLUMN tax_amount REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    conn.close()

@app.route('/api/billing/version', methods=['GET'])
def get_version():
    return jsonify({"version": VERSION, "tax_engine_active": ENABLE_NEW_TAX_ENGINE}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
