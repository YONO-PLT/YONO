import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="YONO", layout="wide", page_icon="📈")

st.title("📊 YONO - منصة تحليل الأسهم الأمريكية")

st.sidebar.header("الإعدادات")
tickers_input = st.sidebar.text_area("أدخل رموز الأسهم (مفصولة بفاصلة)", "AAPL, NVDA, TSLA, AMZN, MSFT")
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if st.sidebar.button("🚀 تحليل الآن"):
    with st.spinner("جاري التحليل..."):
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="1y")
                info = stock.info
                
                sector = info.get('sector', '')
                if any(word in sector for word in ['Financial', 'Bank', 'Insurance']):
                    st.warning(f"⚠️ تم استبعاد {ticker} (قطاع مالي)")
                    continue
                
                df['RSI'] = ta.rsi(df['Close'], length=14)
                macd = ta.macd(df['Close'])
                stoch = ta.stoch(df['High'], df['Low'], df['Close'])
                df = pd.concat([df, macd, stoch], axis=1)
                
                current_price = df['Close'].iloc[-1]
                fair_value = info.get('forwardPE', 20) * info.get('forwardEps', current_price/15)
                
                col1, col2 = st.columns([1,2])
                with col1:
                    st.subheader(ticker)
                    st.metric("السعر الحالي", f"${current_price:.2f}")
                    st.metric("القيمة العادلة", f"${fair_value:.2f}")
                
                with col2:
                    st.write(f"**القطاع:** {sector}")
                    st.write(f"**حجم التداول:** {info.get('volume',0):,}")
                
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"{ticker} - آخر سنة", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("المؤشرات الفنية")
                c1,c2,c3 = st.columns(3)
                c1.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
                c2.metric("MACD", f"{df.get('MACDh_12_26_9', pd.Series([0])).iloc[-1]:.2f}")
                c3.metric("Stochastic", f"{df.get('STOCHk_14_3_3', pd.Series([0])).iloc[-1]:.1f}")
                
            except Exception as e:
                st.error(f"خطأ في {ticker}: {e}")

st.success("✅ YONO جاهزة! أدخل الأسهم واضغط تحليل")
