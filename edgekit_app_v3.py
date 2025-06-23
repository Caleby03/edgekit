
import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="EdgeKit Journal Analyzer", layout="wide")
st.title("📊 EdgeKit Trade Journal Analyzer")

# --- File upload
uploaded_file = st.file_uploader("Upload your trade CSV", type=["csv"])
broker = st.selectbox("Select your broker", ["Webull", "Robinhood", "ThinkorSwim"])

def process_webull(df):
    df = df[df['Status'] == 'Filled'].copy()
    df['Price'] = df['Price'].replace('[\@]', '', regex=True).astype(float)
    df['Side'] = df['Side'].str.lower()
    df['Filled'] = df['Filled'].astype(float)

    trades = []
    positions = {}

    for _, row in df.iterrows():
        symbol = row['Symbol']
        side = row['Side']
        qty = row['Filled']
        price = row['Price']

        if symbol not in positions:
            positions[symbol] = []

        if side == 'buy':
            positions[symbol].append((qty, price))
            trades.append(0.0)
        elif side == 'sell':
            pnl = 0.0
            remaining = qty
            while remaining > 0 and positions[symbol]:
                bought_qty, bought_price = positions[symbol][0]
                matched_qty = min(remaining, bought_qty)
                pnl += matched_qty * (price - bought_price)
                if matched_qty == bought_qty:
                    positions[symbol].pop(0)
                else:
                    positions[symbol][0] = (bought_qty - matched_qty, bought_price)
                remaining -= matched_qty
            trades.append(pnl)
        else:
            trades.append(0.0)

    df['PnL'] = trades
    df['CumulativePnL'] = df['PnL'].cumsum()
    df['Time'] = pd.to_datetime(df['Filled Time'], errors='coerce')
    return df

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        if broker == "Webull":
            df = process_webull(df)
        else:
            st.error(f"Broker '{broker}' is supported in structure but not yet implemented. Coming soon!")
            st.stop()

        st.success("✅ File processed successfully!")
        st.dataframe(df.head(25), use_container_width=True)

        # PnL over time
        st.subheader("📈 Cumulative PnL Over Time")
        fig = px.line(df, x="Time", y="CumulativePnL", title="Cumulative PnL", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Download cleaned CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Cleaned CSV", csv, "edgekit_cleaned.csv", "text/csv")

    except Exception as e:
        st.error(f"There was an error processing your file: {e}")
