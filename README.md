# APS Hazard Risk Dashboard — Alameda County SSA

Real-time Streamlit dashboard mapping APS client vulnerability against
wildfire, flood, and extreme heat hazard zones.

## Local setup

```bash
# 1. Clone / copy this folder
cd aps_dashboard

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place your data file in the same folder as app.py
# File: Vulnerabilities_Report_-_Open_and_Closed_-_Received_01012023-12312025.xlsx
# OR upload via the sidebar file uploader when running the app

# 5. Run
streamlit run app.py
```

## Deploy to Streamlit Cloud (public URL)

1. Push this folder to GitHub: `github.com/Uniqsha448/aps-hazard-dashboard`
2. Go to share.streamlit.io → New app
3. Select repo + `app.py` as entry point
4. Add your Excel file as a GitHub repo file (or use the sidebar uploader)
5. Deploy → live URL in ~2 minutes

## Real-time data updates

The dashboard uses `@st.cache_data(ttl=300)` — it re-reads the Excel file
every 5 minutes automatically. To make it truly real-time:

- Replace the Excel load with a database query (Postgres, Snowflake, etc.)
- Or connect to Alameda County's data API when available
- Enable "Auto-refresh (5 min)" in the sidebar

## Map layers

- **Wildfire WUI**: Based on EOP 2025 Fig. 2-12 · CAL FIRE WUI boundaries
- **Flood zones**: Based on EOP 2025 Fig. 2-8 · FEMA NFIP 100/500-year zones
- **Extreme heat**: Based on NOAA heat index data · Inland valley zones

## To add real GeoJSON boundaries

Replace the approximate circle zones in `HAZARD_ZONES` with:
```python
folium.GeoJson('fema_flood_zones_alameda.geojson', ...).add_to(m)
folium.GeoJson('calfire_wui_alameda.geojson', ...).add_to(m)
```

GeoJSON sources:
- FEMA flood: https://msc.fema.gov/portal/search
- CAL FIRE WUI: https://www.fire.ca.gov/what-we-do/fire-resource-assessment-program/fire-hazard-severity-zones
- Alameda County open data: https://data.acgov.org
