
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide", page_title="EdgeKit v5 - Dynamic Trade Analyzer")
st.title("📈 EdgeKit v5 - Dynamic Trade Analyzer")

@st.cache_data
def clean_data(upload):
    df = pd.read_csv(upload, parse_dates=['EntryTime', 'ExitTime'])
    df['PnL'] = df['PnL'].fillna(0)
    df['DayOfWeek'] = df['EntryTime'].dt.day_name()
    df['HourOfDay'] = df['EntryTime'].dt.hour
    df['DurationMinutes'] = (df['ExitTime'] - df['EntryTime']).dt.total_seconds() / 60
    df['IsWin'] = df['PnL'] > 0
    df['IsLoss'] = df['PnL'] < 0
    df['RiskReward'] = np.where(df['IsLoss'], np.nan, df['PnL'] / df['PnL'][df['PnL'] < 0].mean())
    df['CumulativePnL'] = df['PnL'].cumsum()
    df['Drawdown'] = df['CumulativePnL'] - df['CumulativePnL'].cummax()
    return df

upload = st.file_uploader("📤 Upload your cleaned trade CSV (with EntryTime, ExitTime, PnL, Symbol)", type=["csv"])

if upload:
    df = clean_data(upload)

    with st.sidebar:
        st.header("Filter")
        symbols = df['Symbol'].unique().tolist()
        selected_symbols = st.multiselect("Symbols", symbols, default=symbols)

        days = df['DayOfWeek'].unique().tolist()
        selected_days = st.multiselect("Days of Week", days, default=days)

        hour_min, hour_max = st.slider("Hour Range", 0, 23, (0, 23))

        filtered = df[
            df['Symbol'].isin(selected_symbols) &
            df['DayOfWeek'].isin(selected_days) &
            df['HourOfDay'].between(hour_min, hour_max)
        ]

    st.markdown("## 📊 Performance Charts")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(filtered.groupby('DayOfWeek')['PnL'].sum().reset_index(), x='DayOfWeek', y='PnL', title="PnL by Day of Week"), use_container_width=True)
        st.plotly_chart(px.histogram(filtered, x='DurationMinutes', nbins=30, title="Trade Duration (Minutes)"), use_container_width=True)
        st.plotly_chart(px.bar(filtered.groupby('Symbol')['RiskReward'].mean(numeric_only=True).dropna().reset_index(), x='Symbol', y='RiskReward', title='Risk-Reward Ratio'), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(filtered.groupby('HourOfDay')['PnL'].sum().reset_index(), x='HourOfDay', y='PnL', title="PnL by Hour"), use_container_width=True)
        st.plotly_chart(px.bar(filtered.groupby('DayOfWeek')['IsWin'].mean().reset_index(), x='DayOfWeek', y='IsWin', title="Win Rate by Day"), use_container_width=True)
        st.plotly_chart(px.area(filtered, x='ExitTime', y='Drawdown', title="Max Drawdown Over Time"), use_container_width=True)

    st.plotly_chart(px.histogram(filtered, x='PnL', nbins=50, title="PnL Distribution per Trade"), use_container_width=True)

    win_loss = filtered['IsWin'].value_counts().rename(index={True: 'Win', False: 'Loss'})
    st.plotly_chart(px.pie(values=win_loss.values, names=win_loss.index, title="Win vs Loss Split"), use_container_width=True)

    st.markdown("## 🧾 Trade Log")
    st.dataframe(filtered, use_container_width=True)
else:
    st.info("👆 Please upload a CSV to begin.")
