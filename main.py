from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET")

# Constants
CAPITAL_RS = 10000
CAPITAL_USDT = CAPITAL_RS / 83  # Approx INR→USDT
ALLOCATION = 0.2  # 20% of capital
LEVERAGE = 5
TAKE_PROFIT_PERCENT = 0.10
STOP_LOSS_PERCENT = 0.05

DELTA_BASE_URL = "https://api.delta.exchange"

@app.route('/', methods=['GET'])
def home():
    return 'Webhook is live!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Received Alert:", data)

    signal = data.get("signal")
    symbol = data.get("symbol")
    quantity = data.get("quantity", 0)

    if not signal or not symbol:
        return jsonify({"error": "Missing signal or symbol"}), 400

    # Calculate position size in USDT
    allocated_usdt = CAPITAL_USDT * ALLOCATION
    position_value = allocated_usdt * LEVERAGE

    # Prepare order
    order_payload = {
        "product_symbol": symbol,
        "size": position_value,
        "order_type": "market",
        "side": "buy" if signal == "buy" else "sell",
        "leverage": LEVERAGE,
        "reduce_only": False
    }

    print("📦 Sending order:", order_payload)

    # Make authenticated API call to Delta
    headers = {
        "api-key": DELTA_API_KEY,
        "api-secret": DELTA_API_SECRET,
        "Content-Type": "application/json"
    }

    response = requests.post(f"{DELTA_BASE_URL}/orders/create", json=order_payload, headers=headers)
    print("📨 API Response:", response.status_code, response.text)

    if response.status_code == 200:
        return jsonify({"message": "Order placed"}), 200
    else:
        return jsonify({"error": "Failed to place order", "details": response.text}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
