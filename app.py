import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🔥 BIST PRO ANALİZ PANELİ")

symbol = st.text_input("Hisse Kodu Gir (Örn: FROTO, THYAO, SASA)")

if symbol:
    ticker = yf.Ticker(symbol + ".IS")
    data = ticker.history(period="1y")
    info = ticker.info

    if not data.empty:

        close = data["Close"]

        # RSI Hesaplama
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Moving Average
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        # Grafik
        st.subheader("📈 Fiyat & MA Grafiği")

        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(close, label="Fiyat")
        ax.plot(ma50, label="MA50")
        ax.plot(ma200, label="MA200")
        ax.legend()
        st.pyplot(fig)

        st.subheader("📊 RSI")
        fig2, ax2 = plt.subplots(figsize=(10,3))
        ax2.plot(rsi)
        ax2.axhline(70)
        ax2.axhline(30)
        st.pyplot(fig2)

        price = close.iloc[-1]
        eps = info.get("trailingEps", None)
        book = info.get("bookValue", None)
        roe = info.get("returnOnEquity", None)
        debt_equity = info.get("debtToEquity", None)

        st.subheader("📊 Temel Analiz")

        st.write("Güncel Fiyat:", round(price,2))

        if eps:
            fk = price / eps
            st.write("F/K:", round(fk,2))
        if book:
            pddd = price / book
            st.write("PD/DD:", round(pddd,2))
        if roe:
            st.write("ROE:", round(roe*100,2), "%")
        if debt_equity:
            st.write("Borç/Özsermaye:", round(debt_equity,2))

        # Graham Değeri
        if eps and book:
            graham = np.sqrt(22.5 * eps * book)
            st.write("📌 Graham Değeri:", round(graham,2))

            iskonto = ((graham - price)/graham)*100
            st.write("İskonto Oranı:", round(iskonto,2), "%")

        st.subheader("🤖 Otomatik Yorum")

        if eps and book:
            if price < graham and fk < 15:
                st.success("🟢 Temel olarak UCUZ görünüyor.")
            else:
                st.error("🔴 Temel olarak pahalı görünüyor.")

        if ma50.iloc[-1] > ma200.iloc[-1]:
            st.success("🟢 Golden Cross - Teknik Pozitif")
        else:
            st.error("🔴 Death Cross - Teknik Zayıf")

        if rsi.iloc[-1] < 30:
            st.success("🟢 RSI Aşırı Satım")
        elif rsi.iloc[-1] > 70:
            st.error("🔴 RSI Aşırı Alım")
