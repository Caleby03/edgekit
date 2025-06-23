
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EdgeKit Trade Journal Analyzer", layout="wide")
st.title("📈 EdgeKit Trade Journal Analyzer")

st.sidebar.header("Upload Your Trade CSV")
broker = st.sidebar.selectbox("Select Broker Format", ["Webull", "Robinhood", "ThinkorSwim"])

uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df)} trades from {broker} CSV")

        st.subheader("📊 Trade Overview")
        st.dataframe(df.head(), use_container_width=True)

        if broker == "Webull":
            df_clean = df.rename(columns={
                "Symbol": "Symbol",
                "Side": "Side",
                "Quantity": "Quantity",
                "Price": "Price",
                "Realized PnL": "PnL",
                "Filled Time": "Time",
                "Time": "Time"
            })

        elif broker == "Robinhood":
            df_clean = df.rename(columns={
                "Ticker": "Symbol",
                "Action": "Side",
                "Shares": "Quantity",
                "Price": "Price",
                "Date": "Time",
                "Total Gain/Loss": "PnL"
            })

        elif broker == "ThinkorSwim":
            df_clean = df.rename(columns={
                "Symbol": "Symbol",
                "Side": "Side",
                "Quantity": "Quantity",
                "Price": "Price",
                "Date": "Date",
                "Time": "Clock",
                "P/L Close": "PnL"
            })
            if "Date" in df_clean and "Clock" in df_clean:
                df_clean["Time"] = pd.to_datetime(df_clean["Date"] + " " + df_clean["Clock"], errors="coerce")

        # General time conversion
        if "Time" in df_clean:
            df_clean["Time"] = pd.to_datetime(df_clean["Time"], errors="coerce")
            df_clean = df_clean.dropna(subset=["Time"])

            df_clean = df_clean.sort_values("Time")
            df_clean["CumulativePnL"] = df_clean["PnL"].cumsum()

            st.subheader("📈 Cumulative PnL Over Time")
            fig = px.line(df_clean, x="Time", y="CumulativePnL", color_discrete_sequence=["#00ffaa"])
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("🔍 Symbol Breakdown")
            summary = df_clean.groupby("Symbol")["PnL"].agg(["count", "sum"]).reset_index()
            summary.columns = ["Symbol", "Trades", "TotalPnL"]
            st.dataframe(summary, use_container_width=True)
        else:
            st.warning("Couldn't find a recognizable 'Time' column after mapping.")
    except Exception as e:
        st.error(f"There was an error processing your file: {e}")
else:
    st.info("Upload a CSV file using the sidebar to begin.")

st.markdown("---")
st.caption("EdgeKit - Tools to trade smarter, not harder 🧠")
