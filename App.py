import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 BIST Hisse Analiz Aracı")

symbol = st.text_input("Hisse Kodu (Örn: THYAO, FROTO, SASA)")

if symbol:
    try:
        ticker = yf.Ticker(symbol.upper() + ".IS")
        hist = ticker.history(period="6mo")

        if hist.empty:
            st.error("Hisse bulunamadı.")
        else:
            info = ticker.info

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Güncel Fiyat", round(info.get("currentPrice", 0), 2))

            with col2:
                st.metric("Piyasa Değeri", info.get("marketCap", "Veri yok"))

            with col3:
                st.metric("F/K", info.get("trailingPE", "Veri yok"))

            st.subheader("Son 6 Ay Grafik")

            fig, ax = plt.subplots()
            ax.plot(hist.index, hist["Close"])
            ax.set_xlabel("Tarih")
            ax.set_ylabel("Fiyat")
            st.pyplot(fig)

            st.subheader("Son 5 Günlük Veri")
            st.dataframe(hist.tail())

    except Exception as e:
        st.error("Bir hata oluştu: " + str(e))