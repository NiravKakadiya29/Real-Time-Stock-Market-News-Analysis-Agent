import streamlit as st
import requests
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to fetch stock news
def get_stock_news(stock_symbol):
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("articles", [])[:5]
    else:
        st.error(f"❌ Error fetching news: {response.status_code}")
        return []

# Function to fetch stock info
def get_stock_info(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    info = stock.info
    return {
        "Current Price": info.get("regularMarketPrice", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "52-Week High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52-Week Low": info.get("fiftyTwoWeekLow", "N/A"),
        "PE Ratio": info.get("trailingPE", "N/A"),
        "EPS": info.get("trailingEps", "N/A"),
    }

# Sentiment Analysis
def analyze_sentiment(text):
    if not text:
        return "⚪ No description available"
    sentiment_score = analyzer.polarity_scores(text)["compound"]
    return "🟢 Positive" if sentiment_score > 0.05 else "🔴 Negative" if sentiment_score < -0.05 else "🟡 Neutral"

# AI Summary using OpenAI
def generate_summary(text):
    if not text:
        return None  # Return None instead of message
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": f"Summarize this stock market news:\n{text}"}],
            api_key=OPENAI_API_KEY
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None  # Return None if API fails

# Streamlit UI
st.title("📈 Real-Time Stock Market News & Analysis")
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, NVDA)", "AAPL")

if st.button("Get Stock Info & News"):
    stock_data = get_stock_info(stock_symbol)
    st.subheader("📊 Stock Information")
    for key, value in stock_data.items():
        st.write(f"**{key}:** {value}")
    
    news_articles = get_stock_news(stock_symbol)
    if news_articles:
        st.subheader("📰 Latest News & AI Analysis")
        for article in news_articles:
            st.write(f"### {article['title']}")
            st.write(f"**Source:** {article['source']['name']} | [🔗 Read More]({article['url']})")
            sentiment = analyze_sentiment(article.get("description", ""))
            st.write(f"**Sentiment Analysis:** {sentiment}")
            summary = generate_summary(article.get("description", ""))
            if summary:  # Only display if summary is available
                st.write(f"📝 **AI Summary:** {summary}")
            st.write("---")
