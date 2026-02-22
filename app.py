import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🚀 BIST PRO ANALİZ v3")

symbol = st.text_input("Hisse Kodu (Örn: FROTO, THYAO, SASA)")

if symbol:
    ticker = yf.Ticker(symbol + ".IS")
    data = ticker.history(period="1y")
    info = ticker.info

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
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()

        # Bollinger
        std = close.rolling(20).std()
        upper = ma20 + 2 * std
        lower = ma20 - 2 * std

        # Grafik
        st.subheader("📈 Fiyat + Teknik")
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(close, label="Fiyat")
        ax.plot(ma20, label="MA20")
        ax.plot(ma50, label="MA50")
        ax.plot(ma200, label="MA200")
        ax.plot(upper, linestyle="dashed")
        ax.plot(lower, linestyle="dashed")
        ax.legend()
        st.pyplot(fig)

        st.subheader("📊 RSI & MACD")
        fig2, ax2 = plt.subplots(figsize=(10,4))
        ax2.plot(rsi, label="RSI")
        ax2.axhline(70)
        ax2.axhline(30)
        ax2.legend()
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots(figsize=(10,4))
        ax3.plot(macd, label="MACD")
        ax3.plot(signal, label="Signal")
        ax3.legend()
        st.pyplot(fig3)

        # Temel
        price = close.iloc[-1]
        eps = info.get("trailingEps", None)
        book = info.get("bookValue", None)
        roe = info.get("returnOnEquity", None)

        st.subheader("💰 Temel Analiz")

        score = 0

        if eps:
            fk = price / eps
            st.write("F/K:", round(fk,2))
            if fk < 15:
                score += 20

        if book:
            pddd = price / book
            st.write("PD/DD:", round(pddd,2))
            if pddd < 2:
                score += 20

        if roe:
            st.write("ROE:", round(roe*100,2), "%")
            if roe > 0.15:
                score += 20

        if eps and book:
            graham = np.sqrt(22.5 * eps * book)
            iskonto = ((graham - price)/graham)*100
            st.write("Graham Değeri:", round(graham,2))
            st.write("İskonto %:", round(iskonto,2))
            if iskonto > 20:
                score += 20

        # Teknik skor
        if ma50.iloc[-1] > ma200.iloc[-1]:
            score += 10

        if rsi.iloc[-1] < 30:
            score += 10

        st.subheader("🧠 Genel Skor")

        st.write("Toplam Puan:", score, "/100")

        if score >= 70:
            st.success("🟢 GÜÇLÜ AL")
        elif score >= 50:
            st.info("🟡 AL")
        elif score >= 30:
            st.warning("⚪ NÖTR")
        else:
            st.error("🔴 ZAYIF")
