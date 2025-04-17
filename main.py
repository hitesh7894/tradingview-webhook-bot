from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Delta Exchange API credentials
DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET")

# Capital Settings
TOTAL_CAPITAL = 10000  # ₹
TRADE_PERCENT = 0.20  # 20%
LEVERAGE = 5

@app.route('/', methods=['GET'])
def home():
    return 'Webhook is live!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)

    signal = data.get("signal")
    symbol = data.get("symbol")

    if signal not in ["buy", "sell"] or symbol != "SOLUSDT":
        return "Invalid data", 400

    # Fetch SOLUSDT price from Delta
    price_data = requests.get("https://api.delta.exchange/v2/markets/SOLUSDT").json()
    mark_price = float(price_data["result"]["mark_price"])
    print("Mark Price:", mark_price)

    capital_to_use = TOTAL_CAPITAL * TRADE_PERCENT  # ₹2000
    usdt_amount = capital_to_use * LEVERAGE         # ₹2000 * 5 = ₹10,000 worth
    quantity = round(usdt_amount / mark_price, 4)   # Coin quantity to buy/sell

    side = "buy" if signal == "buy" else "sell"
    stop_loss = round(mark_price * (0.95 if side == "buy" else 1.05), 2)
    take_profit = round(mark_price * (1.10 if side == "buy" else 0.90), 2)

    headers = {
        "api-key": DELTA_API_KEY,
        "Content-Type": "application/json"
    }

    order_payload = {
        "product_id": 132,  # SOLUSDT Perp ID
        "size": quantity,
        "side": side,
        "order_type": "market",
        "time_in_force": "gtc",
        "stop_loss": {"order_type": "market", "stop_price": stop_loss},
        "take_profit": {"order_type": "market", "stop_price": take_profit}
    }

    print("Placing order:", order_payload)
    response = requests.post(
        "https://api.delta.exchange/orders",
        headers=headers,
        json=order_payload
    )

    print("Delta Response:", response.status_code, response.text)
    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
