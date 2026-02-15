import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flight Analytics Dashboard", layout="wide")

st.title("✈️ Flight Delay Analytics Dashboard")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("flights.csv")
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")

airlines = st.sidebar.multiselect(
    "Select Airline",
    options=df["AIRLINE"].unique(),
    default=df["AIRLINE"].unique()
)

df = df[df["AIRLINE"].isin(airlines)]

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", len(df))
col2.metric("Avg Departure Delay", round(df["DEPARTURE_DELAY"].mean(), 2))
col3.metric("Avg Arrival Delay", round(df["ARRIVAL_DELAY"].mean(), 2))
col4.metric("Cancellation Rate (%)", round(df["CANCELLED"].mean() * 100, 2))

st.markdown("---")

# Delay by Airline
st.subheader("Average Arrival Delay by Airline")

delay_airline = df.groupby("AIRLINE")["ARRIVAL_DELAY"].mean().reset_index()

fig1 = px.bar(delay_airline, x="AIRLINE", y="ARRIVAL_DELAY",
              color="ARRIVAL_DELAY",
              title="Avg Arrival Delay per Airline")

st.plotly_chart(fig1, use_container_width=True)

# Monthly Trend
if "MONTH" in df.columns:
    st.subheader("Monthly Delay Trend")
    monthly = df.groupby("MONTH")["ARRIVAL_DELAY"].mean().reset_index()

    fig2 = px.line(monthly, x="MONTH", y="ARRIVAL_DELAY",
                   markers=True,
                   title="Average Arrival Delay per Month")

    st.plotly_chart(fig2, use_container_width=True)

# Busiest Airports
if "ORIGIN_AIRPORT" in df.columns:
    st.subheader("Top 10 Busiest Origin Airports")

    busiest = df["ORIGIN_AIRPORT"].value_counts().head(10).reset_index()
    busiest.columns = ["Airport", "Flights"]

    fig3 = px.bar(busiest, x="Airport", y="Flights",
                  title="Top 10 Airports by Flight Volume")

    st.plotly_chart(fig3, use_container_width=True)
