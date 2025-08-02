import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# -------------------------
# Load and prepare data
# -------------------------
@st.cache_data
def load_crime_data():
    df = pd.read_excel("bristol_crime_sorted.xlsx")
    df = df.rename(columns={'date ': 'month'})
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['year'] = df['month'].dt.year
    df['month_num'] = df['month'].dt.month

    def get_season(m):
        if m in [12, 1, 2]: return 'Winter'
        elif m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        else: return 'Autumn'

    df['season'] = df['month_num'].apply(get_season)
    return df.dropna(subset=['lat', 'lng'])

crime_df = load_crime_data()

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.title("🔍 Filter Crime Data")

year_options = ['All'] + sorted(crime_df['year'].unique())
selected_year = st.sidebar.selectbox("Select Year", year_options)

season_options = ['All', 'Winter', 'Spring', 'Summer', 'Autumn']
selected_season = st.sidebar.selectbox("Select Season", season_options)

crime_types = ['All'] + sorted(crime_df['category'].unique())
selected_crime = st.sidebar.selectbox("Select Crime Type", crime_types)

# -------------------------
# Filter logic
# -------------------------
filtered_df = crime_df.copy()

if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['year'] == selected_year]
if selected_season != 'All':
    filtered_df = filtered_df[filtered_df['season'] == selected_season]
if selected_crime != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_crime]

# -------------------------
# Main UI
# -------------------------
st.title("🔴 Bristol Crime Heatmap")
st.markdown(f"**Crimes Displayed**: {len(filtered_df)}")

# Limit to 10,000 rows for performance
max_points = 10000
if len(filtered_df) > max_points:
    heat_data = filtered_df.sample(max_points)[['lat', 'lng']].values.tolist()
else:
    heat_data = filtered_df[['lat', 'lng']].values.tolist()

# -------------------------
# Create and show map
# -------------------------
m = folium.Map(location=[51.4545, -2.5879], zoom_start=12, tiles="OpenStreetMap")

if heat_data:
    HeatMap(
        heat_data,
        radius=7,
        blur=10,
        gradient={0.2: 'orange', 0.5: 'red', 1: 'darkred'}
    ).add_to(m)
else:
    st.warning("No crime data available for selected filters.")

st_folium(m, width=800, height=600)
