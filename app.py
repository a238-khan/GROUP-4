# Standalone Plotly Dashboard for SafeBristol Visualization
# Save this as app.py and run with: streamlit run app.py
import sys
import pandas as pd
import numpy as np
import webbrowser
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import plotly.express as px
import plotly.graph_objects as go

def open_browser():
    webbrowser.open_new('http://localhost:8503')

# Load data
data_path = 'crimes_api_all_df.csv'
if not os.path.exists(data_path):
    print(f"{data_path} not found. Please export your DataFrame as crimes_api_all_df.csv.")
    exit(1)
crimes_df = pd.read_csv(data_path)

# Filter options (for demo, you can expand to use input())
ward_filter = None  # e.g., 'Ashley'
street_filter = None  # e.g., 'Park Street'
category_filter = None  # e.g., 'burglary'
df = crimes_df.copy()
if ward_filter:
    df = df[df['ward'].astype(str).str.contains(ward_filter, na=False, case=False)]
if street_filter:
    df = df[df['street_name'].astype(str).str.contains(street_filter, na=False, case=False)]
if category_filter:
    df = df[df['category'].astype(str).str.contains(category_filter, na=False, case=False)]

# Plotly visualizations
plots_html = """
<html><head><title>SafeBristol Plotly Dashboard</title></head><body>
<h1>SafeBristol: AI-Powered Crime Prediction & Safety Dashboard (Plotly)</h1>
"""

if not df.empty:
    # Crime Hotspots (Scatter Map)
    fig_map = px.scatter_mapbox(df.sample(min(500, len(df))), lat="lat", lon="lng", color="category",
        hover_data=["ward", "street_name"],
        color_discrete_sequence=px.colors.qualitative.Safe, zoom=11, height=500)
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    plots_html += fig_map.to_html(full_html=False, include_plotlyjs='cdn')

    # Crime Category Distribution
    fig_cat = px.bar(df['category'].value_counts().head(10), labels={'index':'Category', 'value':'Count'}, title='Top 10 Crime Categories')
    plots_html += fig_cat.to_html(full_html=False, include_plotlyjs='cdn')

    # Top 10 Wards
    fig_ward = px.bar(df['ward'].value_counts().head(10), labels={'index':'Ward', 'value':'Count'}, title='Top 10 Wards by Crime Count')
    plots_html += fig_ward.to_html(full_html=False, include_plotlyjs='cdn')

    # Top 10 Streets
    fig_street = px.bar(df['street_name'].value_counts().head(10), labels={'index':'Street', 'value':'Count'}, title='Top 10 Streets by Crime Count')
    plots_html += fig_street.to_html(full_html=False, include_plotlyjs='cdn')

    # Monthly Crime Trend
    if 'year' in df.columns and 'month' in df.columns:
        df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
        trend = df.groupby('year_month').size().reset_index(name='count')
        fig_trend = px.line(trend, x='year_month', y='count', title='Monthly Crime Trend')
        plots_html += fig_trend.to_html(full_html=False, include_plotlyjs='cdn')
else:
    plots_html += '<h3>No crime data available after filtering.</h3>'

plots_html += "</body></html>"

# Write to HTML file
with open('plotly_dashboard.html', 'w') as f:
    f.write(plots_html)

# Serve the HTML file
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/plotly_dashboard.html':
            self.path = '/plotly_dashboard.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server():
    httpd = HTTPServer(('localhost', 8503), Handler)
    print('Serving Plotly dashboard at http://localhost:8503')
    httpd.serve_forever()

threading.Timer(1.5, open_browser).start()
run_server()