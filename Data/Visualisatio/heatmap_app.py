import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

# -------------------------
# Load and preprocess data
# -------------------------
@st.cache_data
def load_crime_data():
    df = pd.read_excel("Data/Visualisatio/bristol_crime_sorted.xlsx")
    df.columns = df.columns.str.strip()

    if "date" in df.columns:
        df.rename(columns={"date": "month"}, inplace=True)
    elif "date " in df.columns:
        df.rename(columns={"date ": "month"}, inplace=True)

    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month

    def get_season(m):
        if m in [12, 1, 2]: return "Winter"
        elif m in [3, 4, 5]: return "Spring"
        elif m in [6, 7, 8]: return "Summer"
        else: return "Autumn"

    df["season"] = df["month_num"].apply(get_season)

    if {"average_rent", "population_density", "deprivation_index"}.issubset(df.columns):
        df["rent_range"] = df["average_rent"].apply(
            lambda r: "< £1000" if r < 1000 else
                      "£1000–£1500" if r < 1500 else
                      "£1500–£2000" if r < 2000 else "> £2000"
        )
        df["population_level"] = df["population_density"].apply(
            lambda p: "Low (<3000)" if p < 3000 else
                      "Medium (3000–7000)" if p < 7000 else "High (>7000)"
        )
        df["deprivation_level"] = df["deprivation_index"].apply(
            lambda d: "Low (0–0.3)" if d < 0.3 else
                      "Medium (0.3–0.6)" if d < 0.6 else "High (0.6–1.0)"
        )

    return df.dropna(subset=["lat", "lng"])

df = load_crime_data()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.title("🔍 Filter Crime Data")

year = st.sidebar.selectbox("Select Year", ["All"] + sorted(df["year"].unique()))
season = st.sidebar.selectbox("Select Season", ["All", "Winter", "Spring", "Summer", "Autumn"])
crime_type = st.sidebar.selectbox("Select Crime Type", ["All"] + sorted(df["category"].dropna().unique()))
street = st.sidebar.selectbox("Select Street Name", ["All"] + sorted(df["street_name"].dropna().unique()))

rent = st.sidebar.selectbox("Select Rent Range", ["All"] + sorted(df["rent_range"].dropna().unique()) if "rent_range" in df else ["All"])
pop = st.sidebar.selectbox("Select Population Level", ["All"] + sorted(df["population_level"].dropna().unique()) if "population_level" in df else ["All"])
dep = st.sidebar.selectbox("Select Deprivation Level", ["All"] + sorted(df["deprivation_level"].dropna().unique()) if "deprivation_level" in df else ["All"])

# -------------------------
# Apply filters
# -------------------------
filtered_df = df.copy()

if year != "All":
    filtered_df = filtered_df[filtered_df["year"] == year]
if season != "All":
    filtered_df = filtered_df[filtered_df["season"] == season]
if crime_type != "All":
    filtered_df = filtered_df[filtered_df["category"] == crime_type]
if street != "All":
    filtered_df = filtered_df[filtered_df["street_name"] == street]
if rent != "All" and "rent_range" in filtered_df:
    filtered_df = filtered_df[filtered_df["rent_range"] == rent]
if pop != "All" and "population_level" in filtered_df:
    filtered_df = filtered_df[filtered_df["population_level"] == pop]
if dep != "All" and "deprivation_level" in filtered_df:
    filtered_df = filtered_df[filtered_df["deprivation_level"] == dep]

# -------------------------
# Show results
# -------------------------
st.title("🔴 Bristol Crime Heatmap + Markers")
st.markdown(f"**Total Crimes Displayed**: {len(filtered_df)}")

m = folium.Map(location=[51.4545, -2.5879], zoom_start=12, tiles="OpenStreetMap")

# Heatmap layer
if not filtered_df.empty:
    heat_data = (
        filtered_df.sample(5000)[["lat", "lng"]].values.tolist()
        if len(filtered_df) > 5000
        else filtered_df[["lat", "lng"]].values.tolist()
    )
    HeatMap(heat_data, radius=7, blur=10, gradient={0.2: "orange", 0.5: "red", 1: "darkred"}).add_to(m)

    # Cluster markers with popup counts
    cluster = MarkerCluster().add_to(m)
    location_counts = filtered_df.groupby(["lat", "lng"]).size()

    for (lat, lng), count in location_counts.items():
        folium.Marker(
            location=[lat, lng],
            popup=f"{count} crime(s) here",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(cluster)
else:
    st.warning("No data found for selected filters.")

st_folium(m, width=800, height=600)
