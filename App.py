import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet

st.set_page_config(layout="wide")
st.title("🔥 BIST PRO MAX v5")

symbol = st.text_input("Hisse Kodu (Örn: FROTO, THYAO, SASA)")

if symbol:
    ticker = yf.Ticker(symbol.upper() + ".IS")
    bist = yf.Ticker("XU100.IS")

    data = ticker.history(period="2y", interval="1d")
    bist_data = bist.history(period="2y", interval="1d")

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

        # Bollinger Bands
        std = close.rolling(20).std()
        upper = ma20 + 2*std
        lower = ma20 - 2*std

        # Trend
        trend = "YUKARI" if ma50.iloc[-1] > ma200.iloc[-1] else "AŞAĞI"

        # Plotly ile interaktif grafik
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=close, mode='lines', name='Close'))
        fig.add_trace(go.Scatter(x=data.index, y=ma50, mode='lines', name='MA50'))
        fig.add_trace(go.Scatter(x=data.index, y=ma200, mode='lines', name='MA200'))
        fig.add_trace(go.Scatter(x=data.index, y=upper, mode='lines', name='Upper BB', line=dict(dash='dash')))
        fig.add_trace(go.Scatter(x=data.index, y=lower, mode='lines', name='Lower BB', line=dict(dash='dash')))

        # Alım/Satım noktaları örneği (MACD)
        buy_signals = (macd > signal) & (macd.shift(1) < signal.shift(1))
        sell_signals = (macd < signal) & (macd.shift(1) > signal.shift(1))

        fig.add_trace(go.Scatter(x=data.index[buy_signals], y=close[buy_signals],
                                 mode='markers', name='AL', marker=dict(color='green', size=10)))
        fig.add_trace(go.Scatter(x=data.index[sell_signals], y=close[sell_signals],
                                 mode='markers', name='SAT', marker=dict(color='red', size=10)))

        st.subheader("📈 Fiyat & Bollinger & Al/Sat")
        st.plotly_chart(fig, use_container_width=True)

        # RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=rsi, name="RSI"))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        st.subheader("📊 RSI")
        st.plotly_chart(fig_rsi, use_container_width=True)

        # Tahmin (Prophet)
        st.subheader("🔮 Gelecek Fiyat Tahmini (1 Ay)")
        df_prophet = close.reset_index()[['Date', 'Close']].rename(columns={'Date':'ds','Close':'y'})
        model = Prophet(daily_seasonality=True)
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Tahmin'))
        fig_forecast.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], mode='lines', name='Gerçek'))
        st.plotly_chart(fig_forecast, use_container_width=True)