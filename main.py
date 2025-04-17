from flask import Flask, request
import os
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET")

BASE_URL = "https://api.delta.exchange"

# Capital & leverage setup
TOTAL_CAPITAL = 10000  # ₹
POSITION_PERCENT = 0.20  # 20% per trade
LEVERAGE = 5

# Contract details
CONTRACT_SYMBOL = "SOLUSD"
CONTRACT_ID = 216  # ID for SOLUSD perpetual (check Delta docs if needed)

@app.route('/', methods=['GET'])
def home():
    return 'Webhook is live!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received signal:", data)

    side = data.get("side")  # "buy" or "sell"
    if side not in ["buy", "sell"]:
        return "Invalid signal", 400

    direction = 1 if side == "buy" else -1
    capital = TOTAL_CAPITAL * POSITION_PERCENT
    margin = capital / LEVERAGE

    # Fetch latest price to calculate size
    price = get_latest_price()
    if price is None:
        return "Failed to get price", 500

    size = round(margin * LEVERAGE / price, 3)  # approx quantity of SOL

    place_order(direction, size, price)

    return "Order Executed", 200


def get_latest_price():
    try:
        response = requests.get(f"{BASE_URL}/v2/tickers/SOLUSD")
        return float(response.json()["result"]["mark_price"])
    except:
        return None

def place_order(direction, size, entry_price):
    timestamp = str(int(time.time() * 1000))

    # Order payload
    body = {
        "contract_id": CONTRACT_ID,
        "size": size,
        "side": "buy" if direction == 1 else "sell",
        "order_type": "market",
        "post_only": False,
        "reduce_only": False,
        "leverage": LEVERAGE
    }

    signature = generate_signature("POST", "/v2/orders", body, timestamp)

    headers = {
        "api-key": DELTA_API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }

    order_url = f"{BASE_URL}/v2/orders"
    res = requests.post(order_url, headers=headers, json=body)
    print("Order response:", res.json())

    # Take-profit and stop-loss
    tp_price = round(entry_price * 1.10, 2)
    sl_price = round(entry_price * 0.95, 2)
    place_exit_order("limit", tp_price, size, direction, True)  # TP
    place_exit_order("stop_market", sl_price, size, direction, True)  # SL

def place_exit_order(order_type, price, size, direction, reduce_only):
    timestamp = str(int(time.time() * 1000))

    body = {
        "contract_id": CONTRACT_ID,
        "size": size,
        "side": "sell" if direction == 1 else "buy",  # reverse side
        "order_type": order_type,
        "price": price if order_type == "limit" else None,
        "stop_price": price if order_type == "stop_market" else None,
        "reduce_only": reduce_only
    }

    signature = generate_signature("POST", "/v2/orders", body, timestamp)

    headers = {
        "api-key": DELTA_API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }

    requests.post(f"{BASE_URL}/v2/orders", headers=headers, json=body)

def generate_signature(method, path, body, timestamp):
    message = f"{timestamp}{method.upper()}{path}{'' if body is None else str(body).replace(' ', '')}"
    return hmac.new(DELTA_API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
