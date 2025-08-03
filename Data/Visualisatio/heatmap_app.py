import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# -------------------------
# Load and preprocess data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Data/Visualisatio/bristol_crime_with_socioeconomic_data.xlsx")
    df.columns = df.columns.str.strip()  # clean spaces in column names

    # Fix column if labeled 'date ' in some versions
    if "date " in df.columns:
        df = df.rename(columns={"date ": "month"})

    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month

    # Add season column
    def get_season(month):
        if month in [12, 1, 2]: return "Winter"
        elif month in [3, 4, 5]: return "Spring"
        elif month in [6, 7, 8]: return "Summer"
        else: return "Autumn"
    df["season"] = df["month_num"].apply(get_season)

    # Add socioeconomic filters if columns exist
    required_cols = {"average_rent", "population_density", "deprivation_index"}
    if required_cols.issubset(df.columns):
        def rent_group(r): return "< £1000" if r < 1000 else "£1000–£1500" if r < 1500 else "£1500–£2000" if r < 2000 else "> £2000"
        def pop_group(p): return "Low (<3000)" if p < 3000 else "Medium (3000–7000)" if p < 7000 else "High (>7000)"
        def dep_group(d): return "Low (0–0.3)" if d < 0.3 else "Medium (0.3–0.6)" if d < 0.6 else "High (0.6–1.0)"

        df["rent_range"] = df["average_rent"].apply(rent_group)
        df["population_level"] = df["population_density"].apply(pop_group)
        df["deprivation_level"] = df["deprivation_index"].apply(dep_group)
    else:
        st.warning("Socioeconomic columns not found. Only basic filters will be shown.")

    return df.dropna(subset=["lat", "lng"])

df = load_data()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.title("🔍 Filter Crime Data")

year = st.sidebar.selectbox("Select Year", ["All"] + sorted(df["year"].unique()))
season = st.sidebar.selectbox("Select Season", ["All", "Winter", "Spring", "Summer", "Autumn"])
crime = st.sidebar.selectbox("Select Crime Type", ["All"] + sorted(df["category"].unique()))

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
if crime != "All":
    filtered_df = filtered_df[filtered_df["category"] == crime]
if "rent_range" in filtered_df and rent != "All":
    filtered_df = filtered_df[filtered_df["rent_range"] == rent]
if "population_level" in filtered_df and pop != "All":
    filtered_df = filtered_df[filtered_df["population_level"] == pop]
if "deprivation_level" in filtered_df and dep != "All":
    filtered_df = filtered_df[filtered_df["deprivation_level"] == dep]

# -------------------------
# Map
# -------------------------
st.title("🔴 Bristol Crime Heatmap (with Socioeconomic Filters)")
st.markdown(f"**Total Crimes Displayed**: {len(filtered_df)}")

m = folium.Map(location=[51.4545, -2.5879], zoom_start=12, tiles="OpenStreetMap")

if not filtered_df.empty:
    heat_data = (
        filtered_df.sample(10000)[["lat", "lng"]].values.tolist()
        if len(filtered_df) > 10000
        else filtered_df[["lat", "lng"]].values.tolist()
    )
    HeatMap(heat_data, radius=7, blur=10, gradient={0.2: "orange", 0.5: "red", 1: "darkred"}).add_to(m)
else:
    st.warning("No crime data found for selected filters.")

st_folium(m, width=800, height=600)
