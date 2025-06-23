
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="EdgeKit Trade Analyzer")

st.title("📊 EdgeKit - Trade Journal Analyzer v4")

# Load enhanced summary
@st.cache_data
def load_data():
    df = pd.read_csv("webull_trade_summary_v4.csv", parse_dates=['EntryTime', 'ExitTime'])
    df['DayOfWeek'] = df['EntryTime'].dt.day_name()
    df['HourOfDay'] = df['EntryTime'].dt.hour
    return df

df = load_data()

# Sidebar Filters
with st.sidebar:
    st.header("Filter Trades")
    symbols = df['Symbol'].unique().tolist()
    selected_symbols = st.multiselect("Symbols", symbols, default=symbols)

    days = df['DayOfWeek'].unique().tolist()
    selected_days = st.multiselect("Days of Week", days, default=days)

    hours = df['HourOfDay'].unique().tolist()
    selected_hours = st.slider("Hour Range", min_value=0, max_value=23, value=(0, 23))

# Apply filters
filtered_df = df[
    df['Symbol'].isin(selected_symbols) &
    df['DayOfWeek'].isin(selected_days) &
    df['HourOfDay'].between(hours[0], hours[1])
]

# Charts
def load_chart(title, filename):
    file_path = f"chart_{filename}.html"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.components.v1.html(f.read(), height=400, scrolling=True)

st.markdown("### Performance Charts")

col1, col2 = st.columns(2)
with col1:
    load_chart("PnL by Day", "pnl_by_day")
    load_chart("Trade Duration", "trade_duration")
    load_chart("Risk Reward Ratio", "risk_reward_ratio")
with col2:
    load_chart("PnL by Hour", "pnl_by_hour")
    load_chart("Win Rate by Day", "win_rate_by_day")
    load_chart("Max Drawdown", "max_drawdown")

st.markdown("---")
st.markdown("### Summary Charts")
load_chart("PnL Histogram", "pnl_histogram")
load_chart("Win/Loss Split", "winloss_split")

st.markdown("---")
st.dataframe(filtered_df, use_container_width=True)
