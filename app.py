import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")

st.title("✈️ Domestic Flight Performance Dashboard")
st.markdown("Analyze airline delays, performance, and airport traffic patterns")

# ==============================
# LOAD DATA
# ==============================

@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    
    # Clean column names
    df.columns = df.columns.str.strip().str.upper()
    
    return df

df = load_data()

st.sidebar.header("🔎 Filter Options")

# ==============================
# AUTO-DETECT IMPORTANT COLUMNS
# ==============================

def detect_column(possible_names):
    for col in possible_names:
        if col in df.columns:
            return col
    return None

airline_col = detect_column(["AIRLINE", "UNIQUECARRIER", "CARRIER"])
arr_delay_col = detect_column(["ARRIVAL_DELAY", "ARRDELAY"])
dep_delay_col = detect_column(["DEPARTURE_DELAY", "DEPDELAY"])
origin_col = detect_column(["ORIGIN_AIRPORT", "ORIGIN"])
month_col = detect_column(["MONTH"])
cancel_col = detect_column(["CANCELLED"])

# ==============================
# SIDEBAR FILTERS
# ==============================

if airline_col:
    selected_airlines = st.sidebar.multiselect(
        "Select Airline",
        options=sorted(df[airline_col].dropna().unique()),
        default=sorted(df[airline_col].dropna().unique())
    )
    df = df[df[airline_col].isin(selected_airlines)]

# ==============================
# KPI SECTION
# ==============================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", f"{len(df):,}")

if dep_delay_col:
    col2.metric("Avg Departure Delay (min)", round(df[dep_delay_col].mean(), 2))

if arr_delay_col:
    col3.metric("Avg Arrival Delay (min)", round(df[arr_delay_col].mean(), 2))

if cancel_col:
    cancellation_rate = df[cancel_col].mean() * 100
    col4.metric("Cancellation Rate (%)", round(cancellation_rate, 2))

st.markdown("---")

# ==============================
# GRAPH SECTION
# ==============================

st.subheader("📊 Visual Analysis")

graph_option = st.selectbox(
    "Select Graph Type",
    [
        "Average Arrival Delay by Airline",
        "Monthly Delay Trend",
        "Top 10 Busiest Airports",
        "Delay Distribution",
        "Departure vs Arrival Delay",
    ]
)

# ---- GRAPH 1 ----
if graph_option == "Average Arrival Delay by Airline" and airline_col and arr_delay_col:
    data = df.groupby(airline_col)[arr_delay_col].mean().reset_index()
    fig = px.bar(
        data,
        x=airline_col,
        y=arr_delay_col,
        color=arr_delay_col,
        title="Average Arrival Delay by Airline",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- GRAPH 2 ----
elif graph_option == "Monthly Delay Trend" and month_col and arr_delay_col:
    data = df.groupby(month_col)[arr_delay_col].mean().reset_index()
    fig = px.line(
        data,
        x=month_col,
        y=arr_delay_col,
        markers=True,
        title="Average Arrival Delay per Month",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- GRAPH 3 ----
elif graph_option == "Top 10 Busiest Airports" and origin_col:
    busiest = df[origin_col].value_counts().head(10).reset_index()
    busiest.columns = ["Airport", "Flights"]
    fig = px.bar(
        busiest,
        x="Airport",
        y="Flights",
        title="Top 10 Busiest Origin Airports",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- GRAPH 4 ----
elif graph_option == "Delay Distribution" and arr_delay_col:
    fig = px.histogram(
        df,
        x=arr_delay_col,
        nbins=50,
        title="Distribution of Arrival Delays",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- GRAPH 5 ----
elif graph_option == "Departure vs Arrival Delay" and arr_delay_col and dep_delay_col:
    fig = px.scatter(
        df.sample(min(2000, len(df))),
        x=dep_delay_col,
        y=arr_delay_col,
        opacity=0.5,
        title="Departure Delay vs Arrival Delay",
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Required columns not found for this visualization.")

st.markdown("---")

# ==============================
# BUSINESS INSIGHTS SECTION
# ==============================

st.subheader("📈 Automatic Insights")

if airline_col and arr_delay_col:
    worst_airline = (
        df.groupby(airline_col)[arr_delay_col].mean().idxmax()
    )
    best_airline = (
        df.groupby(airline_col)[arr_delay_col].mean().idxmin()
    )

    st.success(f"🏆 Best On-Time Airline: **{best_airline}**")
    st.error(f"⚠️ Worst Performing Airline: **{worst_airline}**")

if origin_col:
    busiest_airport = df[origin_col].value_counts().idxmax()
    st.info(f"✈️ Busiest Airport: **{busiest_airport}**")

if arr_delay_col:
    on_time_percentage = (df[arr_delay_col] <= 0).mean() * 100
    st.write(f"🕒 On-Time Arrival Percentage: **{round(on_time_percentage,2)}%**")

st.markdown("---")

# ==============================
# DOWNLOAD OPTION
# ==============================

st.subheader("⬇️ Download Filtered Data")

st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False),
    file_name="filtered_flights.csv",
    mime="text/csv",
)

st.markdown("Developed with ❤️ using Streamlit")
