from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
VERSION = "1.0.0"

def init_db():
    conn = sqlite3.connect('billing.db')
    # V1 Schema: Just id and amount
    conn.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY, amount REAL)")
    conn.commit()
    conn.close()

@app.route('/api/billing/version', methods=['GET'])
def get_version():
    return jsonify({"version": VERSION}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
