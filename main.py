from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Webhook is live!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook received:", data)
    return jsonify({'status': 'success', 'data': data}), 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # 👈 allows external access
        port=int(os.environ.get("PORT", 5000)),  # 👈 use Railway-assigned port
        debug=False
    )

