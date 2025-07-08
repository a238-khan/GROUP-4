# SafeBristol: AI-Powered Crime Prediction & Safety Advisory
# All data is sourced from public APIs (UK Police, Met Office, TfL, user reports placeholder).

import sys
import time
import datetime
try:
    import requests
except ImportError:
    import sys
    import subprocess
    print('requests not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests
try:
    import pandas as pd
except ImportError:
    import sys
    import subprocess
    print('pandas not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
    import pandas as pd
try:
    import numpy as np
except ImportError:
    import sys
    import subprocess
    print('numpy not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])
    import numpy as np
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
except ImportError:
    import sys
    import subprocess
    print('scikit-learn not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scikit-learn'])
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
try:
    import matplotlib.pyplot as plt
except ImportError:
    import sys
    import subprocess
    print('matplotlib not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])
    import matplotlib.pyplot as plt
try:
    import seaborn as sns
except ImportError:
    import sys
    import subprocess
    print('seaborn not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'seaborn'])
    import seaborn as sns

# 1. Fetch Bristol Crime Data from UK Police API (2015-2025, polygon covers city)
bristol_poly = '51.4645,-2.6200:51.4645,-2.5400:51.4300,-2.5400:51.4300,-2.6200'
all_crimes = []
start_year, start_month = 2015, 1
end_year, end_month = 2025, 7
api_url = 'https://data.police.uk/api/crimes-street/all-crime'
for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        if (year == start_year and month < start_month) or (year == end_year and month > end_month):
            continue
        date_str = f"{year}-{month:02d}"
        params = {'poly': bristol_poly, 'date': date_str}
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            crimes = response.json()
            print(f"{date_str}: {len(crimes)} records fetched.")
            all_crimes.extend(crimes)
        elif response.status_code == 404:
            continue
        else:
            print(f"{date_str}: Failed to fetch data. Status code: {response.status_code}")
            print('Response:', response.text)
        time.sleep(1)
all_crimes = [c for c in all_crimes if c is not None]
if all_crimes:
    crimes_df = pd.DataFrame(all_crimes)
    print(f"Total records from Jan 2015 to Jul 2025: {len(crimes_df)}")
else:
    crimes_df = pd.DataFrame()
    print("No data fetched from Jan 2015 to Jul 2025.")

# 2. Clean and Preprocess API Data
if not crimes_df.empty:
    crimes_df = crimes_df.replace(r'^\s*$', np.nan, regex=True)
    crimes_df = crimes_df.dropna(how='all')
    print('After cleaning, shape:', crimes_df.shape)
    print(crimes_df.isnull().sum())
else:
    print('crimes_df is empty, nothing to clean.')

# 3. Feature Engineering (time, location, category)
if not crimes_df.empty:
    crimes_df['category_code'] = crimes_df['category'].astype('category').cat.codes
    crimes_df['month'] = pd.to_datetime(crimes_df['month'], errors='coerce').dt.month.fillna(0).astype(int)
    crimes_df['year'] = pd.to_datetime(crimes_df['month'], errors='coerce').dt.year.fillna(0).astype(int)
    crimes_df['lat'] = crimes_df['location'].apply(lambda x: float(x['latitude']) if isinstance(x, dict) and x.get('latitude') else np.nan)
    crimes_df['lng'] = crimes_df['location'].apply(lambda x: float(x['longitude']) if isinstance(x, dict) and x.get('longitude') else np.nan)
    crimes_df = crimes_df.dropna(subset=['lat', 'lng'])
    print('After feature engineering, shape:', crimes_df.shape)
    crimes_df.head()
else:
    print('crimes_df is empty, nothing to feature engineer.')

# 4. Integrate Weather Data (Met Office API placeholder)
def fetch_weather_for_date(lat, lng, date, api_key='YOUR_API_KEY'):
    return {'weather_condition': np.random.choice(['Clear', 'Rain', 'Cloudy', 'Fog']), 'temperature': np.random.normal(12, 4)}
if not crimes_df.empty:
    crimes_df['weather_condition'] = [fetch_weather_for_date(row['lat'], row['lng'], f"{row['year']}-{row['month']:02d}")['weather_condition'] for idx, row in crimes_df.iterrows()]
    crimes_df['temperature'] = [fetch_weather_for_date(row['lat'], row['lng'], f"{row['year']}-{row['month']:02d}")['temperature'] for idx, row in crimes_df.iterrows()]
    print('Weather data integrated.')
else:
    print('crimes_df is empty, cannot integrate weather data.')

# 5. Integrate Transport Data (TfL API placeholder)
def fetch_tfl_safety_index(lat, lng, date, app_key='YOUR_TFL_APP_KEY'):
    return np.random.uniform(0, 1)
if not crimes_df.empty:
    crimes_df['transport_safety_index'] = [fetch_tfl_safety_index(row['lat'], row['lng'], f"{row['year']}-{row['month']:02d}") for idx, row in crimes_df.iterrows()]
    print('Transport safety data integrated.')
else:
    print('crimes_df is empty, cannot integrate transport data.')

# 6. User-Submitted Safety Reports (Placeholder for API)
def fetch_user_reports(lat, lng, date):
    return np.random.poisson(1)
if not crimes_df.empty:
    crimes_df['user_reports'] = [fetch_user_reports(row['lat'], row['lng'], f"{row['year']}-{row['month']:02d}") for idx, row in crimes_df.iterrows()]
    print('User report data integrated.')
else:
    print('crimes_df is empty, cannot integrate user report data.')

# 7. Machine Learning Model (Random Forest)
if not crimes_df.empty:
    features = ['lat', 'lng', 'month', 'year', 'temperature', 'transport_safety_index', 'user_reports']
    crimes_df['weather_code'] = crimes_df['weather_condition'].astype('category').cat.codes
    features.append('weather_code')
    target = 'category_code'
    X = crimes_df[features]
    y = crimes_df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    print(classification_report(y_test, y_pred))
else:
    print('Not enough data for model training.')

# 8. Advanced ML Model (XGBoost, optional)
try:
    import xgboost
    from xgboost import XGBClassifier
    if not crimes_df.empty:
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
        xgb.fit(X_train, y_train)
        y_pred_xgb = xgb.predict(X_test)
        print('XGBoost Model Performance:')
        print(classification_report(y_test, y_pred_xgb))
except ImportError:
    import sys
    import subprocess
    print('XGBoost not found. Installing...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xgboost'])
    import xgboost
    from xgboost import XGBClassifier
    if not crimes_df.empty:
        xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
        xgb.fit(X_train, y_train)
        y_pred_xgb = xgb.predict(X_test)
        print('XGBoost Model Performance:')
        print(classification_report(y_test, y_pred_xgb))

# 9. Visualize Crime Hotspots (Heatmap)
if not crimes_df.empty:
    plt.figure(figsize=(10, 6))
    sns.kdeplot(x=crimes_df['lng'], y=crimes_df['lat'], cmap='Reds', fill=True, thresh=0.05)
    plt.title('Bristol Crime Hotspots')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()
else:
    print('No geolocation data available for heatmap.')

# 10. Analysis by Wards and Streets in Bristol
if not crimes_df.empty:
    crimes_df['ward'] = crimes_df['location'].apply(lambda x: x.get('ward', None) if isinstance(x, dict) else None)
    crimes_df['street_name'] = crimes_df['location'].apply(lambda x: x['street']['name'] if isinstance(x, dict) and x.get('street') and x['street'].get('name') else None)
    ward_counts = crimes_df['ward'].value_counts(dropna=True)
    print('Top 10 Wards by Crime Count:')
    print(ward_counts.head(10))
    street_counts = crimes_df['street_name'].value_counts(dropna=True)
    print('\nTop 10 Streets by Crime Count:')
    print(street_counts.head(10))
    plt.figure(figsize=(12, 6))
    ward_counts.head(10).plot(kind='bar', color='skyblue')
    plt.title('Top 10 Wards by Crime Count')
    plt.xlabel('Ward')
    plt.ylabel('Number of Crimes')
    plt.show()
    plt.figure(figsize=(12, 6))
    street_counts.head(10).plot(kind='bar', color='salmon')
    plt.title('Top 10 Streets by Crime Count')
    plt.xlabel('Street')
    plt.ylabel('Number of Crimes')
    plt.show()
else:
    print('crimes_df is empty, cannot analyze by ward or street.')

# 11. Next Steps & Integration
print('''\nNext Steps:\n- Integrate real weather, transport, and user report APIs.\n- Use predictions for real-time safety alerts and safe route planning.\n- Connect outputs to the SafeBristol app backend.\n''')

# 12. Streamlit Dashboard for SafeBristol Visualization
# To run: Save this as app.py and run `streamlit run app.py` in your terminal
# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# st.set_page_config(page_title="SafeBristol Crime Dashboard", layout="wide")
# st.title("SafeBristol: Crime Prediction & Safety Dashboard")
# # Load data (assume crimes_df is available or load from a CSV/parquet if needed)
# # For demonstration, you can save crimes_df to a CSV and load here:
# # crimes_df = pd.read_csv('crimes_api_all_df.csv')
# st.sidebar.header("Filters")
# ward_filter = st.sidebar.text_input("Ward (leave blank for all)")
# street_filter = st.sidebar.text_input("Street (leave blank for all)")
# category_filter = st.sidebar.text_input("Crime Category (leave blank for all)")
# df = crimes_df.copy() if 'crimes_df' in globals() else pd.DataFrame()
# if not df.empty:
#     if ward_filter:
#         df = df[df['ward'].str.contains(ward_filter, na=False, case=False)]
#     if street_filter:
#         df = df[df['street_name'].str.contains(street_filter, na=False, case=False)]
#     if category_filter:
#         df = df[df['category'].str.contains(category_filter, na=False, case=False)]
#     st.subheader("Crime Hotspots (Heatmap)")
#     fig, ax = plt.subplots(figsize=(10, 6))
#     sns.kdeplot(x=df['lng'], y=df['lat'], cmap='Reds', fill=True, thresh=0.05, ax=ax)
#     ax.set_title('Bristol Crime Hotspots')
#     ax.set_xlabel('Longitude')
#     ax.set_ylabel('Latitude')
#     st.pyplot(fig)
#     st.subheader("Top 10 Wards by Crime Count")
#     ward_counts = df['ward'].value_counts().head(10)
#     st.bar_chart(ward_counts)
#     st.subheader("Top 10 Streets by Crime Count")
#     street_counts = df['street_name'].value_counts().head(10)
#     st.bar_chart(street_counts)
#     st.subheader("Crime Category Distribution")
#     category_counts = df['category'].value_counts().head(10)
#     st.bar_chart(category_counts)
#     st.subheader("Raw Data Preview")
#     st.dataframe(df.head(100))
# else:
#     st.warning("No crime data available. Please ensure crimes_df is loaded.")

# At the end of your Safebristol-model.py script, export the DataFrame for Streamlit dashboard use
if not crimes_df.empty:
    crimes_df.to_csv('crimes_api_all_df.csv', index=False)
    print('Crime data exported to crimes_api_all_df.csv for Streamlit dashboard.')
