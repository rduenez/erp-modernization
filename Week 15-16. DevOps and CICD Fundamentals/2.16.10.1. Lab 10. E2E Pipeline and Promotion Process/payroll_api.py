from flask import Flask, jsonify
import os

app = Flask(__name__)
ENV = os.environ.get("ENVIRONMENT", "dev")

def calculate_isr(salary):
    # Simulated 2026 ISR Calculation
    return salary * 0.20

@app.route('/api/payroll/calculate', methods=['GET'])
def calculate_payroll():
    salary = 10000
    tax = calculate_isr(salary)
    return jsonify({
        "environment": ENV,
        "base_salary": salary,
        "tax_withheld": tax,
        "net_pay": salary - tax
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
