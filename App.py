import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import feedparser

st.set_page_config(layout="wide")
st.title("📊 BIST PRO MAX v3")

symbol = st.text_input("Hisse Kodu (Örn: THYAO, FROTO, SASA)")

if symbol:
    ticker = yf.Ticker(symbol.upper() + ".IS")
    data = ticker.history(period="6mo")

    if data.empty:
        st.error("Hisse bulunamadı.")
    else:

        close = data["Close"]

        # ================= RSI =================
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # ================= MACD =================
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        data["MACD"] = ema12 - ema26
        data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

        # ================= AL/SAT Sinyali =================
        data["SignalType"] = np.where(
            data["MACD"] > data["Signal"], "AL", "SAT"
        )

        # ================= Mum Grafik =================
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        ))

        # AL SAT okları
        buys = data[data["SignalType"] == "AL"]
        sells = data[data["SignalType"] == "SAT"]

        fig.add_trace(go.Scatter(
            x=buys.index,
            y=buys["Close"],
            mode="markers",
            marker_symbol="triangle-up",
            marker_size=10,
            name="AL"
        ))

        fig.add_trace(go.Scatter(
            x=sells.index,
            y=sells["Close"],
            mode="markers",
            marker_symbol="triangle-down",
            marker_size=10,
            name="SAT"
        ))

        fig.update_layout(
            xaxis_rangeslider_visible=True,
            height=650
        )

        st.plotly_chart(fig, use_container_width=True)

        # ================= Teknik Analiz =================
        if st.button("📊 Teknik Analizi Aç"):
            st.subheader("RSI")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"]))
            fig_rsi.add_hline(y=70)
            fig_rsi.add_hline(y=30)
            st.plotly_chart(fig_rsi, use_container_width=True)

            st.subheader("MACD")
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"]))
            fig_macd.add_trace(go.Scatter(x=data.index, y=data["Signal"]))
            st.plotly_chart(fig_macd, use_container_width=True)

        # ================= KAP HABERLERİ =================
        st.subheader("📰 KAP Haberleri")

        rss_url = f"https://www.kap.org.tr/tr/BildirimRss/{symbol.upper()}"
        feed = feedparser.parse(rss_url)

        if len(feed.entries) == 0:
            st.write("Son KAP bildirimi bulunamadı.")
        else:
            for entry in feed.entries[:5]:
                st.markdown(f"**{entry.title}**")
                st.write(entry.published)
                st.write(entry.link)
                st.write("---")