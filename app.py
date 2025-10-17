from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route('/')
def home():
    return "YFinance API Active ✅"

@app.route('/get_stock')
def get_stock():
    symbol = request.args.get("symbol", "TCS.NS")
    data = yf.download(symbol, period="1d", interval="5m").tail(10).reset_index()
    news = yf.Ticker(symbol).news[:3]
    return jsonify({
        "symbol": symbol,
        "candles": data.to_dict(orient="records"),
        "news": news
    })

if __name__ == "__main__":
    app.run()
