
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def format_hour_label(hour):
    if pd.isna(hour):
        return "Unknown"
    hour = int(hour)
    return datetime.strptime(str(hour), "%H").strftime("%-I %p")

def clean_webull(df):
    df = df.applymap(lambda x: x.replace("@", "") if isinstance(x, str) else x)
    df["Avg Price"] = pd.to_numeric(df["Avg Price"], errors="coerce")
    df["Filled Time"] = pd.to_datetime(df["Filled Time"], format="%m/%d/%Y %H:%M:%S EST", errors="coerce")
    df = df[df["Status"] == "Filled"]
    df = df.dropna(subset=["Avg Price", "Filled Time", "Symbol", "Side"])
    df["Filled Date"] = df["Filled Time"].dt.date
    df["Hour"] = df["Filled Time"].dt.hour
    df["Hour Label"] = df["Hour"].apply(format_hour_label)
    df["Day"] = df["Filled Time"].dt.day_name()
    df["PnL"] = df["Avg Price"] * df["Filled"]
    df["Ticker"] = df["Symbol"]
    df["Trade ID"] = df["Ref #"].astype(str) + "-" + df["Filled Time"].astype(str)
    df["Side"] = df["Side"].astype(str)
    return df

def main():
    st.set_page_config(page_title="EdgeKit Trade Analyzer", layout="wide")
    st.title("📊 EdgeKit Trade Journal Analyzer")

    uploaded_file = st.file_uploader("Upload your trade CSV file", type=["csv"])
    if not uploaded_file:
        st.info("Please upload a CSV file to get started.")
        return

    broker = st.selectbox("Select your broker:", ["Webull", "Robinhood (Coming Soon)", "ThinkorSwim (Coming Soon)"])
    df = pd.read_csv(uploaded_file)

    if broker == "Webull":
        df = clean_webull(df)
    else:
        st.error("Only Webull support is implemented in this version.")
        return

    st.subheader("Trade Log")
    st.dataframe(df[["Filled Time", "Ticker", "Side", "Filled", "Avg Price", "PnL", "Day", "Hour Label"]])

    # Filters
    st.sidebar.header("Filter Trades")
    symbols = st.sidebar.multiselect("Filter by Ticker", options=sorted(df["Ticker"].unique()), default=list(df["Ticker"].unique()))
    days = st.sidebar.multiselect("Filter by Day", options=df["Day"].unique(), default=list(df["Day"].unique()))
    hours = st.sidebar.multiselect("Filter by Hour", options=df["Hour Label"].unique(), default=list(df["Hour Label"].unique()))

    filtered = df[df["Ticker"].isin(symbols) & df["Day"].isin(days) & df["Hour Label"].isin(hours)]

    # Charts
    st.subheader("Charts")

    st.plotly_chart(px.bar(filtered.groupby("Ticker")["PnL"].sum().reset_index(), x="Ticker", y="PnL", title="Total PnL by Ticker"))
    st.plotly_chart(px.bar(filtered["Day"].value_counts().sort_index().reset_index(), x="index", y="Day", title="Trades by Day of Week", labels={"index": "Day", "Day": "Count"}))
    st.plotly_chart(px.bar(filtered["Hour Label"].value_counts().sort_index().reset_index(), x="index", y="Hour Label", title="Trades by Hour", labels={"index": "Hour", "Hour Label": "Count"}))

    st.plotly_chart(px.line(filtered.groupby("Filled Date")["PnL"].sum().cumsum().reset_index(), x="Filled Date", y="PnL", title="Cumulative PnL Over Time"))

if __name__ == "__main__":
    main()
