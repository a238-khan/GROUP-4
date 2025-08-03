import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# -------------------------
# Load and preprocess data
# -------------------------
@st.cache_data
def load_crime_data():
    df = pd.read_excel("Data/Visualisatio/bristol_crime_sorted.xlsx")
    df.columns = df.columns.str.strip()

    if "date" in df.columns:
        df = df.rename(columns={"date": "month"})
    if "date " in df.columns:
        df = df.rename(columns={"date ": "month"})

    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month

    def get_season(m):
        if m in [12, 1, 2]: return "Winter"
        elif m in [3, 4, 5]: return "Spring"
        elif m in [6, 7, 8]: return "Summer"
        else: return "Autumn"
    df["season"] = df["month_num"].apply(get_season)

    return df.dropna(subset=["lat", "lng"])

@st.cache_data
def get_heat_data(df, max_points=5000):
    if len(df) > max_points:
        return df.sample(max_points)[["lat", "lng"]].values.tolist()
    else:
        return df[["lat", "lng"]].values.tolist()

crime_df = load_crime_data()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.title("🔍 Filter Crime Data")

year_options = ["All"] + sorted(crime_df["year"].unique())
selected_year = st.sidebar.selectbox("Select Year", year_options)

season_options = ["All", "Winter", "Spring", "Summer", "Autumn"]
selected_season = st.sidebar.selectbox("Select Season", season_options)

crime_types = ["All"] + sorted(crime_df["category"].dropna().unique())
selected_crime = st.sidebar.selectbox("Select Crime Type", crime_types)

location_types = ["All"] + sorted(crime_df["location_type"].dropna().unique())
selected_location_type = st.sidebar.selectbox("Select Location Type", location_types)

outcomes = ["All"] + sorted(crime_df["outcome_status"].dropna().unique())
selected_outcome = st.sidebar.selectbox("Select Outcome Status", outcomes)

streets = ["All"] + sorted(crime_df["street_name"].dropna().unique())
selected_street = st.sidebar.selectbox("Select Street Name", streets)

# -------------------------
# Apply filters
# -------------------------
filtered_df = crime_df.copy()

if selected_year != "All":
    filtered_df = filtered_df[filtered_df["year"] == selected_year]
if selected_season != "All":
    filtered_df = filtered_df[filtered_df["season"] == selected_season]
if selected_crime != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_crime]
if selected_location_type != "All":
    filtered_df = filtered_df[filtered_df["location_type"] == selected_location_type]
if selected_outcome != "All":
    filtered_df = filtered_df[filtered_df["outcome_status"] == selected_outcome]
if selected_street != "All":
    filtered_df = filtered_df[filtered_df["street_name"] == selected_street]

# -------------------------
# Main UI and Map
# -------------------------
st.title("🔴 Bristol Crime Heatmap")
st.markdown(f"**Total Crimes Displayed**: {len(filtered_df)}")

heat_data = get_heat_data(filtered_df)

m = folium.Map(location=[51.4545, -2.5879], zoom_start=12, tiles="OpenStreetMap")

if heat_data:
    HeatMap(
        heat_data,
        radius=7,
        blur=10,
        gradient={0.2: "orange", 0.5: "red", 1: "darkred"}
    ).add_to(m)
else:
    st.warning("No crime data found for selected filters.")

st_folium(m, width=800, height=600)
