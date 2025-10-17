from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
from gnews import GNews

app = Flask(__name__)

# Initialize GNews
google_news = GNews(language='en', country='IN', period='1d', max_results=5)

@app.route('/')
def home():
    return "YFinance API Active ✅"

@app.route('/get_stock')
def get_stock():
    symbol = request.args.get("symbol", "TCS.NS")

    # Download latest 5-minute candles with auto_adjust explicitly set
    data = yf.download(symbol, period="1d", interval="5m", auto_adjust=True).tail(10).reset_index()

    # Fix multi-index column names (flatten them)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    
    # Keep only useful columns
    candles = data[["Datetime", "Open", "High", "Low", "Close", "Volume"]].copy()
    candles["Datetime"] = candles["Datetime"].astype(str)
    
    # Convert to dict and ensure all values are JSON serializable
    candle_list = candles.to_dict(orient="records")
    
    # Clean up any remaining non-serializable types
    for candle in candle_list:
        for key in candle:
            if pd.isna(candle[key]):
                candle[key] = None
            elif hasattr(candle[key], 'item'):  # numpy types
                candle[key] = candle[key].item()

    # Get latest news using GNews
    news_list = []
    
    try:
        # Get company name from symbol (remove exchange suffix)
        company_name = symbol.split('.')[0]
        
        # Fetch news articles related to the company
        news_items = google_news.get_news(company_name)

        # Extract only the descriptions from the first 5 news items
        news_list = [article.get('description', 'No description') for article in news_items[:5]]

    except Exception as e:
        print(f"Error fetching news: {e}")
        news_list = []

    return jsonify({
        "symbol": symbol,
        "candles": candle_list,
        "news": news_list
    })

if __name__ == "__main__":
    app.run()
