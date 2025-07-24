
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="SafeBristol Crime Heatmap Dashboard", layout="centered")


st.markdown("""
<h1 style='text-align:center; margin-bottom:0.5em;'>SafeBristol: Crime Heatmap Dashboard</h1>
<p style='text-align:center;'>Explore crime patterns in Bristol. Use the sidebar filters to customize the heatmap view by month, year, crime type, season, and location.</p>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")
months = ["All"] + ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
years = ["All"] + [str(y) for y in range(2010, 2026)]
crime_types = ["All", "Anti-social behaviour", "Burglary", "Drugs", "Robbery", "Vehicle crime", "Violence and sexual offences"]
seasons = ["All", "Winter", "Spring", "Summer", "Autumn"]
locations = ["All", "Park Street", "Gloucester Road", "Broadmead", "Stokes Croft", "Clifton", "Bedminster"]

selected_month = st.sidebar.selectbox("Month", months)
selected_year = st.sidebar.selectbox("Year", years)
selected_crime_type = st.sidebar.selectbox("Crime Type", crime_types)
selected_season = st.sidebar.selectbox("Season", seasons)
selected_location = st.sidebar.selectbox("Location", locations)




# Load cleaned data from Excel files
crime_df = pd.read_excel("Data/bristol_crime_cleaned.xlsx")
weather_df = pd.read_excel("Data/bristol_weather_cleaned.xlsx")


# Ensure 'month' and 'year' columns are integers in both DataFrames

# Robustly extract year and month from formats like '2022-12', '2022', '12', etc.
import re
def robust_extract_year(val):
    if pd.isnull(val):
        return None
    if isinstance(val, str):
        match = re.match(r'^(\d{4})', val)
        return int(match.group(1)) if match else None
    try:
        return int(val)
    except Exception:
        return None
def robust_extract_month(val):
    if pd.isnull(val):
        return None
    if isinstance(val, str):
        # Match 'YYYY-MM' or just 'MM'
        match = re.match(r'^(\d{4})-(\d{1,2})$', val)
        if match:
            return int(match.group(2))
        match2 = re.match(r'^(\d{1,2})$', val)
        if match2:
            return int(match2.group(1))
        # Try to find month at end
        match3 = re.search(r'(\d{1,2})$', val)
        if match3:
            return int(match3.group(1))
        return None
    try:
        return int(val)
    except Exception:
        return None
for col in ['year', 'month']:
    if col in crime_df.columns:
        if col == 'year':
            crime_df[col] = crime_df[col].apply(robust_extract_year)
        else:
            crime_df[col] = crime_df[col].apply(robust_extract_month)
    if col in weather_df.columns:
        if col == 'year':
            weather_df[col] = weather_df[col].apply(robust_extract_year)
        else:
            weather_df[col] = weather_df[col].apply(robust_extract_month)

# Merge weather data into crime data if possible (assuming matching columns like 'month', 'year')
if set(['month', 'year']).issubset(crime_df.columns) and set(['month', 'year']).issubset(weather_df.columns):
    df = pd.merge(crime_df, weather_df, on=['month', 'year'], how='left')
else:
    df = crime_df.copy()

# Filter data based on sidebar selections

filtered_df = df.copy()
if selected_month != "All":
    # Convert month name to number if needed
    month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    month_num = month_map.get(selected_month, None)
    if month_num:
        filtered_df = filtered_df[filtered_df['month'] == month_num]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df['year'] == int(selected_year)]
if selected_crime_type != "All":
    filtered_df = filtered_df[filtered_df['category'] == selected_crime_type]
if selected_season != "All":
    filtered_df = filtered_df[filtered_df['season'] == selected_season]
if selected_location != "All":
    filtered_df = filtered_df[filtered_df['location'] == selected_location]




# Heatmap: Crime count by location (lat/lng)

st.markdown("<h2 style='margin-bottom:0.5em; text-align:center;'>Crime Rate Heatmap</h2>", unsafe_allow_html=True)
st.write("Columns in data:", filtered_df.columns.tolist())
# Robustly detect crime count column
crime_count_col = None
for col in filtered_df.columns:
    if col.lower() in ["crime_count", "count", "total_crimes", "crimes", "number_of_crimes", "crimecount"]:
        crime_count_col = col
        break
if not crime_count_col:
    # Try to use category_code if it looks numeric
    if "category_code" in filtered_df.columns and pd.api.types.is_numeric_dtype(filtered_df["category_code"]):
        crime_count_col = "category_code"
    else:
        # Try to use any numeric column except lat/lng
        numeric_cols = [c for c in filtered_df.select_dtypes(include='number').columns if c not in ["lat", "lng"]]
        if numeric_cols:
            crime_count_col = numeric_cols[0]
if not filtered_df.empty and crime_count_col:
    min_crime = filtered_df[crime_count_col].min()
    max_crime = filtered_df[crime_count_col].max()
    heatmap_fig = px.density_map(
        filtered_df,
        lat="lat",
        lon="lng",
        z=crime_count_col,
        radius=30,
        center=dict(lat=51.4545, lon=-2.5879),
        zoom=12,
        map_style="carto-positron",
        color_continuous_scale=["yellow", "orange", "red"],
        range_color=(min_crime, max_crime),
        title="Crime Rate Heatmap",
        height=800,
        width=1200,
    )
    heatmap_fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(heatmap_fig, use_container_width=True)
elif not crime_count_col:
    st.error("No column for crime count found. Please check your data. Columns: " + str(filtered_df.columns.tolist()))
else:
    st.info("No data available for the selected filters.")


# Optional: Weather-Crime correlation heatmap

st.markdown("<h3 style='margin-bottom:0.5em;'>Weather-Crime Correlation Heatmap</h3>", unsafe_allow_html=True)
weather_temp_col = None
weather_precip_col = None
for col in filtered_df.columns:
    if col.lower() in ["temperature", "temperature_max"]:
        weather_temp_col = col
    if col.lower() in ["precipitation", "precipitation_sum"]:
        weather_precip_col = col
if not filtered_df.empty and crime_count_col and weather_temp_col and weather_precip_col:
    pivot = filtered_df.pivot_table(index=weather_temp_col, columns=weather_precip_col, values=crime_count_col, aggfunc="sum")
    corr_fig = px.imshow(
        pivot,
        labels=dict(x="Precipitation (mm)", y="Temperature (°C)", color="Crime Count"),
        color_continuous_scale="Viridis",
        title="Crime Count by Temperature and Precipitation"
    )
    st.plotly_chart(corr_fig, use_container_width=True)
elif not (weather_temp_col and weather_precip_col):
    st.error("No temperature or precipitation columns found for weather-crime correlation. Columns: " + str(filtered_df.columns.tolist()))
elif not crime_count_col:
    st.error("No column for crime count found for weather-crime correlation. Columns: " + str(filtered_df.columns.tolist()))
else:
    st.info("No weather-crime data available for the selected filters.")
