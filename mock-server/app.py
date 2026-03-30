from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Load JSON file
file_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

with open(file_path) as f:
    customers = json.load(f)


@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    start = (page - 1) * limit
    end = start + limit

    data = customers[start:end]

    return jsonify({
        "data": data,
        "total": len(customers),
        "page": page,
        "limit": limit
    })


@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    for c in customers:
        if c["customer_id"] == customer_id:
            return jsonify(c)

    return jsonify({"error": "Not found"}), 404


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)