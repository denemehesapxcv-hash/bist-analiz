import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🔥 BIST PRO MAX v4")

symbol = st.text_input("Hisse Kodu (Örn: FROTO, THYAO, SASA)")

if symbol:
    ticker = yf.Ticker(symbol.upper() + ".IS")
    bist = yf.Ticker("XU100.IS")

    data = ticker.history(period="2y")
    bist_data = bist.history(period="2y")

    if not data.empty:

        close = data["Close"]
        volume = data["Volume"]

        # Moving averages
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        rsi = 100 - (100/(1+rs))

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()

        # Bollinger
        std = close.rolling(20).std()
        upper = ma20 + 2*std
        lower = ma20 - 2*std

        # Trend
        if ma50.iloc[-1] > ma200.iloc[-1]:
            trend = "YUKARI"
        else:
            trend = "AŞAĞI"

        st.subheader("📈 Fiyat & Bollinger")
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(close)
        ax.plot(ma50)
        ax.plot(ma200)
        ax.plot(upper, linestyle="dashed")
        ax.plot(lower, linestyle="dashed")
        st.pyplot(fig)

        st.subheader("📊 MACD")
        fig2, ax2 = plt.subplots(figsize=(10,4))
        ax2.plot(macd)
        ax2.plot(signal)
        st.pyplot(fig2)

        st.subheader("📊 RSI")
        fig3, ax3 = plt.subplots(figsize=(10,4))
        ax3.plot(rsi)
        ax3.axhline(70)
        ax3.axhline(30)
        st.pyplot(fig3)

        # Performans karşılaştırma
        perf_stock = (close.iloc[-1]/close.iloc[0]-1)*100
        perf_bist = (bist_data["Close"].iloc[-1]/bist_data["Close"].iloc[0]-1)*100

        st.subheader("📊 Endeks Karşılaştırma")
        st.write("Hisse 2Y Getiri:", round(perf_stock,2), "%")
        st.write("BIST100 2Y Getiri:", round(perf_bist,2), "%")

        # Risk
        volatility = close.pct_change().std()*np.sqrt(252)
        st.write("Volatilite:", round(volatility*100,2), "%")

        # Temel
        info = ticker.info
        price = close.iloc[-1]
        eps = info.get("trailingEps", None)
        book = info.get("bookValue", None)

        score = 0

        if eps:
            fk = price/eps
            st.write("F/K:", round(fk,2))
            if fk < 15: score += 15

        if book:
            pddd = price/book
            st.write("PD/DD:", round(pddd,2))
            if pddd < 2: score += 15

        if trend == "YUKARI": score += 20
        if rsi.iloc[-1] < 30: score += 10
        if macd.iloc[-1] > signal.iloc[-1]: score += 10

        if perf_stock > perf_bist: score += 10

        st.subheader("🧠 Genel Yatırım Skoru")
        st.write("Skor:", score, "/100")

        if score >= 70:
            st.success("🟢 GÜÇLÜ AL")
        elif score >= 50:
            st.info("🟡 AL")
        elif score >= 30:
            st.warning("⚪ NÖTR")
        else:
            st.error("🔴 RİSKLİ")
