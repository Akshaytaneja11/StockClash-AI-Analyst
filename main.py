import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="StockClash AI", page_icon="⚔️", layout="wide")

st.title("⚔️ StockClash: AI Financial Duel")
st.markdown("Compare two stocks and let Gemini AI declare the winner.")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get it from Google AI Studio")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        ticker1 = st.text_input("Stock 1", "AAPL").upper()
    with col2:
        ticker2 = st.text_input("Stock 2", "MSFT").upper()
        
    analyze_btn = st.button("Analyze Rivalry 🚀")

# --- CORE FUNCTIONS ---
def get_stock_info(ticker_symbol):
    """Fetches key metrics using yfinance"""
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        # Return a simplified dictionary
        return {
            "Name": info.get('longName', ticker_symbol),
            "Price": info.get('currentPrice', 0),
            "PE Ratio": info.get('forwardPE', 'N/A'),
            "Market Cap": info.get('marketCap', 0),
            "Revenue Growth": info.get('revenueGrowth', 0),
            "52W High": info.get('fiftyTwoWeekHigh', 0),
            "Summary": info.get('longBusinessSummary', 'No summary available.')[:500] + "..."
        }
    except Exception as e:
        return None

def get_ai_analysis(data1, data2, api_key):
    """Sends structured data to Gemini for comparison"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a Senior Financial Analyst. Compare these two companies based on the data provided:
    
    Company A: {data1['Name']}
    - P/E Ratio: {data1['PE Ratio']}
    - Revenue Growth: {data1['Revenue Growth']}
    - Market Cap: {data1['Market Cap']}
    
    Company B: {data2['Name']}
    - P/E Ratio: {data2['PE Ratio']}
    - Revenue Growth: {data2['Revenue Growth']}
    - Market Cap: {data2['Market Cap']}
    
    Compare them on Valuation and Growth Prospects. 
    Be concise. Use bullet points. 
    Conclude with: "Winner for Long-Term Hold: [Company Name]" and explain why.
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- MAIN APP LOGIC ---
if analyze_btn:
    if not api_key:
        st.error("🚨 Please enter your Gemini API Key in the sidebar!")
    else:
        with st.spinner("Fetching Market Data..."):
            stock1_data = get_stock_info(ticker1)
            stock2_data = get_stock_info(ticker2)
        
        if stock1_data and stock2_data:
            # 1. DISPLAY METRICS
            st.subheader("📊 The Tale of the Tape")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.info(f"**{stock1_data['Name']}**")
                st.metric("Price", f"${stock1_data['Price']}")
                st.metric("P/E Ratio", stock1_data['PE Ratio'])
                
            with col_b:
                st.success(f"**{stock2_data['Name']}**")
                st.metric("Price", f"${stock2_data['Price']}")
                st.metric("P/E Ratio", stock2_data['PE Ratio'])

            st.divider()

            # 2. AI ANALYSIS
            st.subheader("🤖 Gemini's Verdict")
            with st.spinner("Gemini is analyzing the balance sheets..."):
                try:
                    analysis = get_ai_analysis(stock1_data, stock2_data, api_key)
                    st.markdown(analysis)
                except Exception as e:
                    st.error(f"AI Error: {e}")

        else:
            st.error("Could not fetch data. Check ticker symbols.")
