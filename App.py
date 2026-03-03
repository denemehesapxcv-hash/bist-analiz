import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 BIST PRO MAX (RSI + MACD + AL/SAT + Yatırımcı Dağılımı)")

symbol = st.text_input("Hisse Kodu (Örn: THYAO, FROTO, SASA)")

if symbol:
    try:
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
            rsi = 100 - (100 / (1 + rs))
            data["RSI"] = rsi

            # ================= MACD =================
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()

            data["MACD"] = macd
            data["Signal"] = signal

            # ================= AL / SAT Yorumu =================
            latest_rsi = data["RSI"].iloc[-1]
            latest_macd = data["MACD"].iloc[-1]
            latest_signal = data["Signal"].iloc[-1]

            st.subheader("📌 Teknik Durum")

            if latest_rsi < 30:
                st.write("RSI: AŞIRI SATIM (Yukarı tepki gelebilir)")
            elif latest_rsi > 70:
                st.write("RSI: AŞIRI ALIM (Düzeltme riski)")
            else:
                st.write("RSI: Nötr")

            if latest_macd > latest_signal:
                st.write("MACD: AL Sinyali")
            else:
                st.write("MACD: SAT Sinyali")

            # ================= Fiyat Grafiği =================
            st.subheader("📈 Fiyat Grafiği")

            fig1, ax1 = plt.subplots()
            ax1.plot(data.index, close)
            ax1.set_xlabel("Tarih")
            ax1.set_ylabel("Fiyat")
            st.pyplot(fig1)

            # ================= RSI Grafiği =================
            st.subheader("📊 RSI Grafiği")

            fig2, ax2 = plt.subplots()
            ax2.plot(data.index, data["RSI"])
            ax2.axhline(70)
            ax2.axhline(30)
            ax2.set_xlabel("Tarih")
            ax2.set_ylabel("RSI")
            st.pyplot(fig2)

            # ================= MACD Grafiği =================
            st.subheader("📊 MACD Grafiği")

            fig3, ax3 = plt.subplots()
            ax3.plot(data.index, data["MACD"])
            ax3.plot(data.index, data["Signal"])
            ax3.set_xlabel("Tarih")
            ax3.set_ylabel("MACD")
            st.pyplot(fig3)

            # ================= Yatırımcı Dağılımı =================
            st.subheader("🥧 Yatırımcı Dağılımı")

            info = ticker.info

            institutions = info.get("heldPercentInstitutions", 0)
            insiders = info.get("heldPercentInsiders", 0)

            institutions = institutions if institutions else 0
            insiders = insiders if insiders else 0

            others = 1 - (institutions + insiders)
            if others < 0:
                others = 0

            labels = ["Kurumlar", "İçeriden Sahiplik", "Diğer (Bireysel/Fon)"]
            sizes = [institutions * 100, insiders * 100, others * 100]

            fig4, ax4 = plt.subplots()
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%')
            st.pyplot(fig4)

    except Exception as e:
        st.error("Bir hata oluştu: " + str(e))