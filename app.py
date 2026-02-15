import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Dashboard", layout="wide")
st.title("✈️ Flight Performance Analytics")

@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# Show columns for debugging
st.sidebar.write("Detected Columns:")
st.sidebar.write(df.columns.tolist())

# ------------------------------------
# SMART COLUMN DETECTION
# ------------------------------------

def find_column(keyword_list):
    for col in df.columns:
        for keyword in keyword_list:
            if keyword in col:
                return col
    return None

airline_col = find_column(["airline", "carrier"])
arr_delay_col = find_column(["arr", "arrival"])
dep_delay_col = find_column(["dep", "departure"])
origin_col = find_column(["origin"])
month_col = find_column(["month"])
cancel_col = find_column(["cancel"])

# ------------------------------------
# FILTER
# ------------------------------------

if airline_col:
    airlines = st.sidebar.multiselect(
        "Select Airline",
        df[airline_col].dropna().unique(),
        default=df[airline_col].dropna().unique(),
    )
    df = df[df[airline_col].isin(airlines)]

# ------------------------------------
# KPI SECTION
# ------------------------------------

st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", len(df))

if dep_delay_col:
    col2.metric("Avg Departure Delay", round(df[dep_delay_col].mean(), 2))

if arr_delay_col:
    col3.metric("Avg Arrival Delay", round(df[arr_delay_col].mean(), 2))

if cancel_col:
    col4.metric("Cancellation Rate (%)", round(df[cancel_col].mean() * 100, 2))

st.markdown("---")

# ------------------------------------
# GRAPH OPTIONS
# ------------------------------------

st.subheader("📊 Visualizations")

option = st.selectbox(
    "Choose Analysis",
    [
        "Airline Delay Comparison",
        "Monthly Trend",
        "Busiest Airports",
        "Delay Distribution",
        "Departure vs Arrival Delay",
    ],
)

# Airline Delay
if option == "Airline Delay Comparison" and airline_col and arr_delay_col:
    data = df.groupby(airline_col)[arr_delay_col].mean().reset_index()
    fig = px.bar(data, x=airline_col, y=arr_delay_col,
                 title="Average Arrival Delay by Airline")
    st.plotly_chart(fig, use_container_width=True)

# Monthly Trend
elif option == "Monthly Trend" and month_col and arr_delay_col:
    data = df.groupby(month_col)[arr_delay_col].mean().reset_index()
    fig = px.line(data, x=month_col, y=arr_delay_col,
                  markers=True,
                  title="Monthly Average Arrival Delay")
    st.plotly_chart(fig, use_container_width=True)

# Busiest Airports
elif option == "Busiest Airports" and origin_col:
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

# Scatter
elif option == "Departure vs Arrival Delay" and arr_delay_col and dep_delay_col:
    sample = df.sample(min(2000, len(df)))
    fig = px.scatter(sample, x=dep_delay_col, y=arr_delay_col,
                     title="Departure vs Arrival Delay",
                     opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Some required columns are missing in this dataset.")

# ------------------------------------
# INSIGHTS
# ------------------------------------

st.markdown("---")
st.subheader("📈 Insights")

if airline_col and arr_delay_col:
    worst = df.groupby(airline_col)[arr_delay_col].mean().idxmax()
    best = df.groupby(airline_col)[arr_delay_col].mean().idxmin()
    st.success(f"Best On-Time Airline: {best}")
    st.error(f"Worst Performing Airline: {worst}")

if origin_col:
    busiest_airport = df[origin_col].value_counts().idxmax()
    st.info(f"Busiest Airport: {busiest_airport}")

if arr_delay_col:
    on_time = (df[arr_delay_col] <= 0).mean() * 100
    st.write(f"On-Time Arrival Rate: {round(on_time,2)}%")
