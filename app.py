import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")
st.title("✈️ Domestic Flight Performance Dashboard")

# ==============================
# LOAD DATA
# ==============================

@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# ==============================
# SMART COLUMN DETECTION
# ==============================

def find_column(keywords):
    for col in df.columns:
        for word in keywords:
            if word in col:
                return col
    return None

airline_col = find_column(["airline", "carrier"])
arr_delay_col = find_column(["arr", "arrival"])
dep_delay_col = find_column(["dep", "departure"])
origin_col = find_column(["origin"])
month_col = find_column(["month"])
cancel_col = find_column(["cancel"])

# ==============================
# CLEAN NUMERIC COLUMNS SAFELY
# ==============================

def clean_numeric(column):
    if column:
        df[column] = pd.to_numeric(df[column], errors="coerce")

clean_numeric(arr_delay_col)
clean_numeric(dep_delay_col)
clean_numeric(cancel_col)

# ==============================
# SIDEBAR FILTER
# ==============================

st.sidebar.header("Filter Options")

if airline_col:
    airlines = st.sidebar.multiselect(
        "Select Airline",
        sorted(df[airline_col].dropna().unique()),
        default=sorted(df[airline_col].dropna().unique()),
    )
    df = df[df[airline_col].isin(airlines)]

# ==============================
# KPI SECTION
# ==============================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", f"{len(df):,}")

if dep_delay_col:
    col2.metric(
        "Avg Departure Delay (min)",
        round(df[dep_delay_col].mean(skipna=True), 2),
    )

if arr_delay_col:
    col3.metric(
        "Avg Arrival Delay (min)",
        round(df[arr_delay_col].mean(skipna=True), 2),
    )

if cancel_col:
    col4.metric(
        "Cancellation Rate (%)",
        round(df[cancel_col].mean(skipna=True) * 100, 2),
    )

st.markdown("---")

# ==============================
# GRAPH OPTIONS
# ==============================

st.subheader("📊 Visual Analysis")

option = st.selectbox(
    "Choose Analysis",
    [
        "Airline Delay Comparison",
        "Monthly Delay Trend",
        "Top 10 Busiest Airports",
        "Delay Distribution",
        "Departure vs Arrival Delay",
    ],
)

# Airline Delay Comparison
if option == "Airline Delay Comparison" and airline_col and arr_delay_col:
    data = df.groupby(airline_col)[arr_delay_col].mean().reset_index()
    fig = px.bar(data, x=airline_col, y=arr_delay_col,
                 title="Average Arrival Delay by Airline")
    st.plotly_chart(fig, use_container_width=True)

# Monthly Trend
elif option == "Monthly Delay Trend" and month_col and arr_delay_col:
    data = df.groupby(month_col)[arr_delay_col].mean().reset_index()
    fig = px.line(data, x=month_col, y=arr_delay_col,
                  markers=True,
                  title="Monthly Average Arrival Delay")
    st.plotly_chart(fig, use_container_width=True)

# Busiest Airports
elif option == "Top 10 Busiest Airports" and origin_col:
    busiest = df[origin_col].value_counts().head(10).reset_index()
    busiest.columns = ["Airport", "Flights"]
    fig = px.bar(busiest, x="Airport", y="Flights",
                 title="Top 10 Busiest Airports")
    st.plotly_chart(fig, use_container_width=True)

# Delay Distribution
elif option == "Delay Distribution" and arr_delay_col:
    fig = px.histogram(df, x=arr_delay_col,
                       title="Arrival Delay Distribution",
                       nbins=50)
    st.plotly_chart(fig, use_container_width=True)

# Scatter Plot
elif option == "Departure vs Arrival Delay" and arr_delay_col and dep_delay_col:
    sample = df.sample(min(2000, len(df)))
    fig = px.scatter(sample,
                     x=dep_delay_col,
                     y=arr_delay_col,
                     opacity=0.5,
                     title="Departure vs Arrival Delay")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Some required columns are missing for this analysis.")

# ==============================
# INSIGHTS SECTION
# ==============================

# ==============================
# INSIGHTS SECTION (SAFE VERSION)
# ==============================

st.markdown("---")
st.subheader("📈 Automated Insights")

# Airline performance insight
if airline_col and arr_delay_col:

    valid_data = df[[airline_col, arr_delay_col]].dropna()

    if not valid_data.empty:
        performance = valid_data.groupby(airline_col)[arr_delay_col].mean()

        if not performance.empty:
            best_airline = performance.idxmin()
            worst_airline = performance.idxmax()

            st.success(f"🏆 Best On-Time Airline: {best_airline}")
            st.error(f"⚠️ Worst Performing Airline: {worst_airline}")
        else:
            st.warning("Not enough delay data for airline comparison.")
    else:
        st.warning("Arrival delay data is missing.")

# Busiest airport insight
if origin_col:
    airport_counts = df[origin_col].dropna()

    if not airport_counts.empty:
        busiest_airport = airport_counts.value_counts().idxmax()
        st.info(f"✈️ Busiest Airport: {busiest_airport}")

# On-time performance
if arr_delay_col:
    valid_arr = df[arr_delay_col].dropna()

    if not valid_arr.empty:
        on_time = (valid_arr <= 0).mean() * 100
        st.write(f"🕒 On-Time Arrival Rate: {round(on_time, 2)}%")
