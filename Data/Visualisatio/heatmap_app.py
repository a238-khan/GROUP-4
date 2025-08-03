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
    df = pd.read_excel("Data/Visualisatio/bristol_crime_with_socioeconomic_data.xlsx")
    df.columns = df.columns.str.strip()

    # Rename if needed
    if "date" in df.columns:
        df.rename(columns={"date": "month"}, inplace=True)
    elif "date " in df.columns:
        df.rename(columns={"date ": "month"}, inplace=True)

    # Date conversion
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['year'] = df['month'].dt.year
    df['month_num'] = df['month'].dt.month

    # Add season
    def get_season(m):
        if m in [12, 1, 2]: return 'Winter'
        elif m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        else: return 'Autumn'

    df['season'] = df['month_num'].apply(get_season)

    # Socioeconomic categorization
    if {'average_rent', 'population_density', 'deprivation_index'}.issubset(df.columns):
        df['rent_range'] = df['average_rent'].apply(
            lambda r: "< £1000" if r < 1000 else
                      "£1000–£1500" if r < 1500 else
                      "£1500–£2000" if r < 2000 else "> £2000"
        )
        df['population_level'] = df['population_density'].apply(
            lambda p: "Low (<3000)" if p < 3000 else
                      "Medium (3000–7000)" if p < 7000 else "High (>7000)"
        )
        df['deprivation_level'] = df['deprivation_index'].apply(
            lambda d: "Low (0–0.3)" if d < 0.3 else
                      "Medium (0.3–0.6)" if d < 0.6 else "High (0.6–1.0)"
        )

    return df.dropna(subset=['lat', 'lng'])

@st.cache_data
def get_heat_data(df, max_points=5000):
    if len(df) > max_points:
        return df.sample(max_points)[['lat', 'lng']].values.tolist()
    else:
        return df[['lat', 'lng']].values.tolist()

crime_df = load_crime_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.title("🔍 Filter Crime Data")

year_options = ['All'] + sorted(crime_df['year'].unique())
selected_year = st.sidebar.selectbox("Select Year", year_options)

season_options = ['All', 'Winter', 'Spring', 'Summer', 'Autumn']
selected_season = st.sidebar.selectbox("Select Season", season_options)

crime_types = ['All'] + sorted(crime_df['category'].dropna().unique())
selected_crime = st.sidebar.selectbox("Select Crime Type", crime_types)

street_names = ['All'] + sorted(crime_df['street_name'].dropna().unique())
selected_street = st.sidebar.selectbox("Select Street Name", street_names)

rent_ranges = ['All'] + sorted(crime_df['rent_range'].dropna().unique()) if 'rent_range' in crime_df else ['All']
selected_rent = st.sidebar.selectbox("Select Rent Range", rent_ranges)

population_levels = ['All'] + sorted(crime_df['population_level'].dropna().unique()) if 'population_level' in crime_df else ['All']
selected_pop = st.sidebar.selectbox("Select Population Level", population_levels)

deprivation_levels = ['All'] + sorted(crime_df['deprivation_level'].dropna().unique()) if 'deprivation_level' in crime_df else ['All']
selected_dep = st.sidebar.selectbox("Select Deprivation Level", deprivation_levels)

# -------------------------
# Apply Filters
# -------------------------
filtered_df = crime_df.copy()

if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['year'] == selected_year]
if selected_season != 'All':
    filtered_df = filtered_df[filtered_df['season'] == selected_season]
if selected_crime != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_crime]
if selected_street != 'All':
    filtered_df = filtered_df[filtered_df['street_name'] == selected_street]
if selected_rent != 'All' and 'rent_range' in filtered_df:
    filtered_df = filtered_df[filtered_df['rent_range'] == selected_rent]
if selected_pop != 'All' and 'population_level' in filtered_df:
    filtered_df = filtered_df[filtered_df['population_level'] == selected_pop]
if selected_dep != 'All' and 'deprivation_level' in filtered_df:
    filtered_df = filtered_df[filtered_df['deprivation_level'] == selected_dep]

# -------------------------
# Main UI
# -------------------------
st.title("🔴 Bristol Crime Heatmap")
st.markdown(f"**Crimes Displayed**: {len(filtered_df)}")

heat_data = get_heat_data(filtered_df)

# -------------------------
# Show Heatmap
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
