import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 BIST PRO ANALİZ (1-2 Kuralı + Yatırımcı Dağılımı)")

symbol = st.text_input("Hisse Kodu (Örn: THYAO, FROTO, SASA)")

if symbol:
    try:
        ticker = yf.Ticker(symbol.upper() + ".IS")
        data = ticker.history(period="6mo")

        if data.empty:
            st.error("Hisse bulunamadı.")
        else:
            close = data["Close"]

            # ===== EMA 50 =====
            data["EMA50"] = close.ewm(span=50, adjust=False).mean()

            # ===== RSI =====
            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            data["RSI"] = 100 - (100 / (1 + rs))

            # ===== MACD =====
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            data["MACD"] = ema12 - ema26
            data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

            # ===== Son Değerler =====
            latest_rsi = data["RSI"].iloc[-1]
            latest_macd = data["MACD"].iloc[-1]
            latest_signal = data["Signal"].iloc[-1]
            latest_price = close.iloc[-1]
            latest_ema = data["EMA50"].iloc[-1]

            st.subheader("📌 1-2 Kuralı Teknik Sonuç")

            if (latest_rsi > 50) and (latest_macd > latest_signal) and (latest_price > latest_ema):
                st.success("🔥 GÜÇLÜ AL SİNYALİ")
            elif (latest_rsi < 50) and (latest_macd < latest_signal) and (latest_price < latest_ema):
                st.error("❌ GÜÇLÜ SAT SİNYALİ")
            else:
                st.warning("⚖️ KARARSIZ / BEKLE")

            # ===== FİYAT GRAFİĞİ =====
            st.subheader("📈 Fiyat + EMA50")
            fig1, ax1 = plt.subplots()
            ax1.plot(data.index, close, label="Fiyat")
            ax1.plot(data.index, data["EMA50"], label="EMA50 (Trend)")
            ax1.legend()
            st.pyplot(fig1)

            # ===== RSI =====
            st.subheader("📊 RSI Göstergesi")
            fig2, ax2 = plt.subplots()
            ax2.plot(data.index, data["RSI"], label="RSI Çizgisi")
            ax2.axhline(70, linestyle="--", label="70 = Aşırı Alım")
            ax2.axhline(30, linestyle="--", label="30 = Aşırı Satım")
            ax2.axhline(50, linestyle="--", label="50 = Trend Dengesi")
            ax2.legend()
            st.pyplot(fig2)

            # ===== MACD =====
            st.subheader("📊 MACD Göstergesi")
            fig3, ax3 = plt.subplots()
            ax3.plot(data.index, data["MACD"], label="MACD Çizgisi")
            ax3.plot(data.index, data["Signal"], label="Signal Çizgisi")
            ax3.legend()
            st.pyplot(fig3)

            st.write("MACD Çizgisi Signal üstüne çıkarsa → AL")
            st.write("MACD Çizgisi Signal altına inerse → SAT")

            # ===== YATIRIMCI DAĞILIMI =====
            st.subheader("🥧 Yatırımcı Dağılımı")

            info = ticker.info

            institutions = info.get("heldPercentInstitutions", 0) or 0
            insiders = info.get("heldPercentInsiders", 0) or 0
            others = 1 - (institutions + insiders)

            if others < 0:
                others = 0

            labels = ["Kurumsal", "İçeriden Sahiplik", "Diğer (Bireysel/Fon)"]
            sizes = [institutions * 100, insiders * 100, others * 100]

            fig4, ax4 = plt.subplots()
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig4)

    except Exception as e:
        st.error("Hata: " + str(e))