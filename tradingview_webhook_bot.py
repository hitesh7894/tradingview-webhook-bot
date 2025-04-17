from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import requests
import json

app = Flask(__name__)

# Replace these with your Delta Exchange API credentials
API_KEY = 'YOUR_API_KEY_HERE'
API_SECRET = 'YOUR_API_SECRET_HERE'

BASE_URL = 'https://api.delta.exchange'

def generate_signature(timestamp, method, request_path, body):
    message = f'{timestamp}{method}{request_path}{body}'
    signature = hmac.new(
        bytes(API_SECRET, 'utf-8'),
        msg=bytes(message, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature

def place_order(product_id, side, size, price=None):
    endpoint = '/v2/orders'
    url = BASE_URL + endpoint

    timestamp = str(int(time.time() * 1000))
    body = {
        'product_id': product_id,
        'side': side,
        'order_type': 'market',
        'size': size
    }

    body_json = json.dumps(body, separators=(',', ':'))
    signature = generate_signature(timestamp, 'POST', endpoint, body_json)

    headers = {
        'api-key': API_KEY,
        'timestamp': timestamp,
        'signature': signature,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=body_json)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)

    # Extract action and size from TradingView alert message
    action = data.get('action')  # 'buy' or 'sell'
    size = int(data.get('size', 1))
    product_id = int(data.get('product_id'))  # example: 105 (for SOLUSD)

    if action in ['buy', 'sell']:
        order_response = place_order(product_id, action, size)
        return jsonify(order_response)
    else:
        return jsonify({'error': 'Invalid action'}), 400

if __name__ == '__main__':
    app.run(port=5000)
