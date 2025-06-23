
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
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Avg Price"] = pd.to_numeric(df["Avg Price"], errors="coerce")
    df["Filled Time"] = pd.to_datetime(df["Filled Time"], format="%m/%d/%Y %H:%M:%S EST", errors="coerce")
    df = df[df["Status"] == "Filled"]
    df = df.dropna(subset=["Price", "Filled Time", "Symbol", "Side"])
    df["Filled Date"] = df["Filled Time"].dt.date
    df["Hour"] = df["Filled Time"].dt.hour
    df["Hour Label"] = df["Hour"].apply(format_hour_label)
    df["Day"] = df["Filled Time"].dt.day_name()
    df["PnL"] = df["Price"] * df["Filled"]
    return df

def main():
    st.set_page_config(page_title="EdgeKit Trade Analyzer", layout="wide")
    st.title("📊 EdgeKit Trade Journal Analyzer")

    uploaded_file = st.file_uploader("Upload your trade CSV file", type=["csv"])
    if not uploaded_file:
        st.info("Please upload a CSV file to get started.")
        return

    broker = st.selectbox("Select your broker:", ["Webull", "Robinhood", "ThinkorSwim"])
    df = pd.read_csv(uploaded_file)

    if broker == "Webull":
        df = clean_webull(df)
    else:
        st.error("Only Webull support is available in this build.")
        return

    st.subheader("Filtered Trade Log")
    st.dataframe(df)

    st.subheader("Total PnL by Symbol")
    pnl_by_symbol = df.groupby("Symbol")["PnL"].sum().reset_index()
    st.plotly_chart(px.bar(pnl_by_symbol, x="Symbol", y="PnL", title="PnL by Symbol"))

    st.subheader("Trades by Day of Week")
    trades_by_day = df["Day"].value_counts().sort_index()
    st.plotly_chart(px.bar(x=trades_by_day.index, y=trades_by_day.values,
                           labels={"x": "Day", "y": "Trades"},
                           title="Trades by Day"))

    st.subheader("Trades by Hour")
    trades_by_hour = df["Hour Label"].value_counts().sort_index()
    st.plotly_chart(px.bar(x=trades_by_hour.index, y=trades_by_hour.values,
                           labels={"x": "Hour", "y": "Trades"},
                           title="Trades by Hour"))

if __name__ == "__main__":
    main()
