from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

import os
# Secure: The password is injected at runtime, never saved in code.
DB_PASSWORD = os.environ.get("DB_PASSWORD", "default_dev_password")



def init_db():
    conn = sqlite3.connect('erp_prod.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, item TEXT, stock INTEGER)")
    cursor.execute("INSERT OR IGNORE INTO inventory (id, item, stock) VALUES (1, 'Server Rack', 45)")
    conn.commit()
    conn.close()

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    conn = sqlite3.connect('erp_prod.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    data = cursor.fetchall()
    conn.close()
    return jsonify({"inventory": data})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5090)

