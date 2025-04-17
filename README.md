# TradingView Webhook Bot
This bot listens to TradingView alerts and executes trades via exchange API.
# 📡 TradingView Webhook Bot

A Python-based bot that listens to [TradingView](https://tradingview.com) webhook alerts and executes trades via exchange APIs (e.g., Delta Exchange, Binance, etc.).

## 🚀 Features

- Accepts webhook alerts from TradingView
- Parses and validates incoming signals
- Executes market orders through exchange APIs
- Simple to configure and deploy

## ⚙️ Requirements

- Python 3.x
- Flask
- Exchange API keys (e.g., Delta, Binance)

## 📦 Setup

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/tradingview-webhook-bot.git
   cd tradingview-webhook-bot

## 🧪 Usage

Once the bot is running:

1. **Create an alert in TradingView**
2. In the alert settings:
   - Set the alert action to **Webhook URL**
   - Paste your bot’s server URL (e.g., `http://yourserver.com/webhook`)
   - In the alert message, send a JSON like:

```json
{
  "symbol": "BTCUSD",
  "side": "buy",
  "quantity": 1
}
