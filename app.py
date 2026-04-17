import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="APS Hazard Risk Dashboard · Alameda County",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (McKinsey monochrome) ─────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    [data-testid="stMetric"] { background: #F5F5F5; border-radius: 6px; padding: 12px 16px; }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #1C1C1C !important; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; color: #6B6B6B !important; }
    .dash-title { font-size: 22px; font-weight: 600; color: #1C1C1C; margin-bottom: 0; }
    .dash-sub { font-size: 12px; color: #6B6B6B; margin-bottom: 1rem; }
    .live-badge { display: inline-block; background: #1A7A4A; color: white;
                  font-size: 10px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
    .section-head { font-size: 13px; font-weight: 600; color: #2E2E2E;
                    border-bottom: 1px solid #EBEBEB; padding-bottom: 4px; margin: 0.75rem 0 0.5rem; }
    .risk-fire { background: #FCEBEB; border-left: 3px solid #E24B4A;
                 border-radius: 4px; padding: 8px 12px; font-size: 12px; margin-bottom: 6px; }
    .risk-flood { background: #E6F1FB; border-left: 3px solid #378ADD;
                  border-radius: 4px; padding: 8px 12px; font-size: 12px; margin-bottom: 6px; }
    .risk-heat { background: #FAEEDA; border-left: 3px solid #BA7517;
                 border-radius: 4px; padding: 8px 12px; font-size: 12px; margin-bottom: 6px; }
    div[data-testid="stSidebarContent"] { background: #F5F5F5; }
    .stSelectbox label { font-size: 12px; color: #4A4A4A; }
    .stMultiSelect label { font-size: 12px; color: #4A4A4A; }
    .timestamp { font-size: 10px; color: #9E9E9E; }
</style>
""", unsafe_allow_html=True)

# ── Zip → coordinates + hazard zones ─────────────────────────────────────────
ZIP_GEO = {
    '94501': (37.7652, -122.2416, 'flood',  'low',   'low'),
    '94502': (37.7369, -122.2268, 'flood',  'low',   'low'),
    '94536': (37.5557, -121.9760, 'low',    'flood', 'heat'),
    '94538': (37.5055, -121.9561, 'low',    'flood', 'heat'),
    '94539': (37.5369, -121.9196, 'low',    'low',   'heat'),
    '94541': (37.6688, -122.0808, 'fire',   'low',   'heat'),
    '94542': (37.6560, -122.0530, 'fire',   'low',   'heat'),
    '94544': (37.6316, -122.0652, 'low',    'flood', 'heat'),
    '94545': (37.6132, -122.0852, 'low',    'flood', 'heat'),
    '94546': (37.6952, -122.0394, 'fire',   'fire',  'heat'),
    '94550': (37.6819, -121.7680, 'fire',   'low',   'heat'),
    '94551': (37.7052, -121.7369, 'fire',   'low',   'heat'),
    '94552': (37.7019, -121.9930, 'fire',   'low',   'heat'),
    '94555': (37.5735, -122.0530, 'low',    'flood', 'heat'),
    '94560': (37.5219, -122.0394, 'low',    'flood', 'heat'),
    '94566': (37.6619, -121.8747, 'fire',   'low',   'heat'),
    '94568': (37.7019, -121.9196, 'fire',   'low',   'heat'),
    '94577': (37.7252, -122.1560, 'low',    'flood', 'low'),
    '94578': (37.7052, -122.1252, 'low',    'flood', 'low'),
    '94579': (37.6852, -122.1469, 'low',    'flood', 'low'),
    '94580': (37.6769, -122.1196, 'fire',   'flood', 'low'),
    '94586': (37.5952, -121.8930, 'fire',   'low',   'heat'),
    '94587': (37.5919, -122.0196, 'low',    'flood', 'heat'),
    '94588': (37.6952, -121.9196, 'fire',   'low',   'heat'),
    '94601': (37.7769, -122.2130, 'low',    'flood', 'heat'),
    '94602': (37.7952, -122.2052, 'fire',   'low',   'low'),
    '94603': (37.7369, -122.1930, 'low',    'low',   'heat'),
    '94605': (37.7569, -122.1730, 'low',    'flood', 'heat'),
    '94606': (37.7852, -122.2369, 'low',    'low',   'heat'),
    '94607': (37.8052, -122.2930, 'low',    'flood', 'low'),
    '94608': (37.8319, -122.2852, 'low',    'flood', 'low'),
    '94609': (37.8319, -122.2569, 'low',    'low',   'low'),
    '94610': (37.8119, -122.2369, 'low',    'low',   'low'),
    '94611': (37.8369, -122.2130, 'fire',   'low',   'low'),
    '94612': (37.8119, -122.2730, 'low',    'low',   'low'),
    '94619': (37.7769, -122.1730, 'fire',   'low',   'low'),
    '94621': (37.7469, -122.1930, 'low',    'flood', 'heat'),
    '94706': (37.8869, -122.2969, 'low',    'flood', 'low'),
    '94707': (37.8919, -122.2769, 'low',    'low',   'low'),
    '94708': (37.8919, -122.2569, 'fire',   'low',   'low'),
    '94709': (37.8769, -122.2669, 'low',    'low',   'low'),
    '94710': (37.8619, -122.3069, 'low',    'flood', 'low'),
}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # refresh every 5 minutes (real-time hook)
def load_data(file_path: str):
    xl = pd.ExcelFile(file_path)
    df = pd.read_excel(xl, sheet_name='Raw_Open+Closed-NoNames')

    # Clean
    df['Zip_clean'] = pd.to_numeric(df['Zip Code'], errors='coerce')
    df['Zip_clean'] = df['Zip_clean'].astype('Int64').astype(str).str[:5]
    df['City_clean'] = df['City'].str.strip().str.title()
    df['Report_Date'] = pd.to_datetime(df['Report Received Date'], errors='coerce')
    df['Close_Date'] = pd.to_datetime(df['Close Date'], errors='coerce')

    # Deduplicate to unique clients
    clients = df.sort_values('Report_Date').drop_duplicates(subset='Client ID', keep='last').copy()

    # Pivot vulnerabilities
    vuln = df[['Client ID', 'Vulnerabilities']].dropna()
    vuln_dum = pd.get_dummies(vuln, columns=['Vulnerabilities'])
    vuln_agg = vuln_dum.groupby('Client ID').max().reset_index()

    clients = clients.merge(vuln_agg, on='Client ID', how='left')
    clients.columns = [c.replace('Vulnerabilities_', 'vuln_').replace(' ', '_') for c in clients.columns]

    # Attach geo + hazard zones
    def get_geo(z):
        return ZIP_GEO.get(str(z), None)

    clients['geo'] = clients['Zip_clean'].apply(get_geo)
    clients['lat'] = clients['geo'].apply(lambda g: g[0] if g else None)
    clients['lon'] = clients['geo'].apply(lambda g: g[1] if g else None)
    clients['hazard_fire']  = clients['geo'].apply(lambda g: g[2] == 'fire' if g else False)
    clients['hazard_flood'] = clients['geo'].apply(lambda g: g[3] == 'flood' if g else False)
    clients['hazard_heat']  = clients['geo'].apply(lambda g: g[4] == 'heat' if g else False)
    clients['hazard_count'] = clients['hazard_fire'].astype(int) + clients['hazard_flood'].astype(int) + clients['hazard_heat'].astype(int)
    clients['lives_alone_flag'] = clients['Lives_Alone'].astype(str).str.lower().isin(['yes', 'true', '1'])

    return clients

# ── Determine file path ───────────────────────────────────────────────────────
DATA_PATH = '/mnt/user-data/uploads/Vulnerabilities_Report_-_Open_and_Closed_-_Received_01012023-12312025.xlsx'

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗂 Data source")

    if os.path.exists(DATA_PATH):
        df_raw = load_data(DATA_PATH)
        st.success(f"Loaded: {len(df_raw):,} unique clients")
    else:
        uploaded = st.file_uploader("Upload APS Excel file", type=['xlsx'])
        if uploaded:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
                f.write(uploaded.read())
                DATA_PATH = f.name
            df_raw = load_data(DATA_PATH)
            st.success(f"Loaded: {len(df_raw):,} unique clients")
        else:
            st.warning("Upload APS Excel to begin")
            st.stop()

    st.markdown("---")
    st.markdown("### 🎛 Filters")

    status_filter = st.selectbox("Case status", ["All", "Open only", "Closed only"])
    hazard_filter = st.multiselect(
        "Show hazard zones",
        ["Wildfire WUI", "Flood zone", "Extreme heat"],
        default=["Wildfire WUI", "Flood zone", "Extreme heat"]
    )
    alone_filter = st.checkbox("Lives alone only", value=False)
    city_options = ["All"] + sorted(df_raw['City_clean'].dropna().unique().tolist())
    city_filter = st.selectbox("City", city_options)

    vuln_cols = [c for c in df_raw.columns if c.startswith('vuln_') and c != 'vuln_Home_Safe_-_Internal_use_only']
    vuln_labels = {c: c.replace('vuln_', '').replace('_', ' ').title() for c in vuln_cols}
    selected_vuln = st.multiselect(
        "Vulnerability type",
        options=list(vuln_labels.keys()),
        format_func=lambda x: vuln_labels[x],
        default=[]
    )

    st.markdown("---")
    st.markdown("### 🗺 Map layer")
    map_view = st.radio("Display mode", ["Client dots", "Heat density", "Both"], index=0)
    auto_refresh = st.checkbox("Auto-refresh (5 min)", value=False)

    st.markdown("---")
    st.markdown(f"<span class='timestamp'>Last updated: {datetime.now().strftime('%b %d %Y · %H:%M')}</span>", unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = df_raw.copy()

if status_filter == "Open only":
    df = df[df['Open_or_Closed'] == 'Open']
elif status_filter == "Closed only":
    df = df[df['Open_or_Closed'] == 'Closed']

if alone_filter:
    df = df[df['lives_alone_flag']]

if city_filter != "All":
    df = df[df['City_clean'] == city_filter]

if selected_vuln:
    mask = df[selected_vuln].eq(True).any(axis=1)
    df = df[mask]

df_mapped = df[df['lat'].notna() & df['lon'].notna()].copy()

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([5, 1])
with col_title:
    st.markdown(
        '<div class="dash-title">APS Client Vulnerability & Hazard Risk Dashboard'
        '<span class="live-badge">● LIVE</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="dash-sub">Alameda County Social Services Agency · '
        f'{len(df):,} clients shown of {len(df_raw):,} total · '
        f'Jan 2023 – Sep 2025</div>',
        unsafe_allow_html=True
    )

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

open_ct = (df['Open_or_Closed'] == 'Open').sum()
alone_ct = df['lives_alone_flag'].sum()
fire_ct  = df['hazard_fire'].sum()
flood_ct = df['hazard_flood'].sum()
heat_ct  = df['hazard_heat'].sum()
triple_ct = (df['hazard_count'] == 3).sum()

k1.metric("Clients shown", f"{len(df):,}")
k2.metric("Open cases", f"{open_ct:,}", f"{open_ct/len(df)*100:.0f}%" if len(df) else "")
k3.metric("Live alone", f"{alone_ct:,}")
k4.metric("🔴 Wildfire risk", f"{fire_ct:,}")
k5.metric("🔵 Flood risk", f"{flood_ct:,}")
k6.metric("🟠 Heat risk", f"{heat_ct:,}")

st.markdown("")

# ── Map + sidebar stats layout ────────────────────────────────────────────────
map_col, stat_col = st.columns([3, 1])

# ── Build Folium map ─────────────────────────────────────────────────────────
with map_col:
    st.markdown('<div class="section-head">Live hazard risk map — APS clients by location</div>', unsafe_allow_html=True)

    m = folium.Map(
        location=[37.72, -122.08],
        zoom_start=11,
        tiles='CartoDB positron',
        prefer_canvas=True
    )

    # ── Hazard zone circles (approximate boundaries) ──────────────────────────
    HAZARD_ZONES = {
        'Wildfire WUI': {
            'active': 'Wildfire WUI' in hazard_filter,
            'color': '#E24B4A',
            'zones': [
                {'name': 'Oakland Hills', 'lat': 37.815, 'lon': -122.195, 'r': 2800},
                {'name': 'Hayward Hills',  'lat': 37.668, 'lon': -122.053, 'r': 3200},
                {'name': 'Castro Valley', 'lat': 37.695, 'lon': -122.039, 'r': 2500},
                {'name': 'Livermore',     'lat': 37.682, 'lon': -121.768, 'r': 3500},
                {'name': 'Pleasanton',    'lat': 37.662, 'lon': -121.874, 'r': 2800},
                {'name': 'Dublin Hills',  'lat': 37.702, 'lon': -121.936, 'r': 2200},
                {'name': 'Sunol',         'lat': 37.595, 'lon': -121.893, 'r': 2000},
                {'name': 'Berkeley Hills','lat': 37.892, 'lon': -122.257, 'r': 1800},
            ]
        },
        'Flood zone': {
            'active': 'Flood zone' in hazard_filter,
            'color': '#378ADD',
            'zones': [
                {'name': 'Alameda Island', 'lat': 37.765, 'lon': -122.242, 'r': 3200},
                {'name': 'Hayward Bay',    'lat': 37.625, 'lon': -122.100, 'r': 3000},
                {'name': 'Newark/Union C', 'lat': 37.540, 'lon': -122.030, 'r': 3200},
                {'name': 'Fremont Bay',    'lat': 37.513, 'lon': -122.052, 'r': 2800},
                {'name': 'San Leandro',    'lat': 37.710, 'lon': -122.155, 'r': 2200},
                {'name': 'Oakland Port',   'lat': 37.798, 'lon': -122.285, 'r': 2000},
                {'name': 'San Lorenzo',    'lat': 37.677, 'lon': -122.120, 'r': 1800},
            ]
        },
        'Extreme heat': {
            'active': 'Extreme heat' in hazard_filter,
            'color': '#EF9F27',
            'zones': [
                {'name': 'Livermore Valley', 'lat': 37.682, 'lon': -121.768, 'r': 4500},
                {'name': 'Pleasanton-Dublin','lat': 37.700, 'lon': -121.880, 'r': 3800},
                {'name': 'Fremont Inland',   'lat': 37.530, 'lon': -121.970, 'r': 3200},
                {'name': 'Castro Valley',    'lat': 37.695, 'lon': -122.039, 'r': 2500},
                {'name': 'Oakland Flatlands','lat': 37.760, 'lon': -122.195, 'r': 3000},
                {'name': 'Hayward Inland',   'lat': 37.660, 'lon': -122.065, 'r': 2800},
            ]
        }
    }

    for hname, hinfo in HAZARD_ZONES.items():
        if hinfo['active']:
            for z in hinfo['zones']:
                folium.Circle(
                    location=[z['lat'], z['lon']],
                    radius=z['r'],
                    color=hinfo['color'],
                    fill=True,
                    fill_opacity=0.12,
                    weight=1.5,
                    opacity=0.6,
                    tooltip=f"<b>{hname}</b><br>{z['name']}"
                ).add_to(m)

    # ── Client markers ────────────────────────────────────────────────────────
    def get_marker_color(row):
        if row['hazard_count'] == 3: return '#7D1C1C'
        if row['hazard_fire']:  return '#E24B4A'
        if row['hazard_flood']: return '#378ADD'
        if row['hazard_heat']:  return '#BA7517'
        return '#6B6B6B'

    def get_risk_label(row):
        parts = []
        if row['hazard_fire']:  parts.append('🔴 Wildfire')
        if row['hazard_flood']: parts.append('🔵 Flood')
        if row['hazard_heat']:  parts.append('🟠 Heat')
        return ', '.join(parts) if parts else 'No mapped hazard'

    def vuln_list(row):
        v = []
        for c in vuln_cols:
            if row.get(c) == True or row.get(c) == 1:
                v.append(vuln_labels[c])
        return ', '.join(v) if v else 'None recorded'

    # Aggregate by zip for performance
    zip_agg = df_mapped.groupby('Zip_clean').agg(
        lat=('lat', 'first'),
        lon=('lon', 'first'),
        client_count=('Client_ID', 'count'),
        open_cases=('Open_or_Closed', lambda x: (x=='Open').sum()),
        lives_alone=('lives_alone_flag', 'sum'),
        hazard_fire=('hazard_fire', 'first'),
        hazard_flood=('hazard_flood', 'first'),
        hazard_heat=('hazard_heat', 'first'),
        hazard_count=('hazard_count', 'first'),
        city=('City_clean', 'first'),
    ).reset_index()

    if map_view in ['Client dots', 'Both']:
        for _, row in zip_agg.iterrows():
            # Risk badges in popup
            hazards_html = ''
            if row['hazard_fire']:  hazards_html += '<span style="background:#FCEBEB;color:#A32D2D;padding:1px 6px;border-radius:4px;font-size:10px;margin-right:3px">🔴 Wildfire</span>'
            if row['hazard_flood']: hazards_html += '<span style="background:#E6F1FB;color:#185FA5;padding:1px 6px;border-radius:4px;font-size:10px;margin-right:3px">🔵 Flood</span>'
            if row['hazard_heat']:  hazards_html += '<span style="background:#FAEEDA;color:#854F0B;padding:1px 6px;border-radius:4px;font-size:10px">🟠 Heat</span>'
            if not hazards_html: hazards_html = '<span style="color:#888;font-size:10px">No mapped hazard</span>'

            # Color by worst hazard
            if row['hazard_count'] == 3:
                dot_color = '#7D1C1C'
            elif row['hazard_fire']:
                dot_color = '#E24B4A'
            elif row['hazard_flood']:
                dot_color = '#378ADD'
            elif row['hazard_heat']:
                dot_color = '#BA7517'
            else:
                dot_color = '#6B6B6B'

            # Size by client count
            radius = max(6, min(22, int(row['client_count'] ** 0.55)))

            popup_html = f"""
            <div style="font-family:Arial;min-width:180px;font-size:12px">
              <b style="font-size:13px">Zip {row['Zip_clean']}</b> &nbsp;{row['city']}<br>
              <hr style="margin:4px 0;border-color:#eee">
              <b>{int(row['client_count'])}</b> APS clients<br>
              <b style="color:#CC0000">{int(row['open_cases'])}</b> open cases<br>
              <b>{int(row['lives_alone'])}</b> live alone<br>
              <hr style="margin:4px 0;border-color:#eee">
              {hazards_html}
            </div>"""

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                color=dot_color,
                fill=True,
                fill_color=dot_color,
                fill_opacity=0.75,
                weight=1.5,
                popup=folium.Popup(popup_html, max_width=240),
                tooltip=f"Zip {row['Zip_clean']} · {int(row['client_count'])} clients"
            ).add_to(m)

    if map_view in ['Heat density', 'Both']:
        heat_data = [[row['lat'], row['lon'], row['client_count']]
                     for _, row in zip_agg.iterrows()]
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_zoom=14,
            radius=25,
            blur=20,
            gradient={'0.4': '#4A4A4A', '0.65': '#888780', '1.0': '#1C1C1C'}
        ).add_to(m)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:10px 14px;border-radius:6px;
                border:1px solid #ddd;font-size:11px;font-family:Arial;
                box-shadow:0 2px 6px rgba(0,0,0,0.1)">
      <b style="font-size:12px">APS client risk</b><br>
      <span style="color:#7D1C1C">⬤</span> All 3 hazards<br>
      <span style="color:#E24B4A">⬤</span> Wildfire zone<br>
      <span style="color:#378ADD">⬤</span> Flood zone<br>
      <span style="color:#BA7517">⬤</span> Extreme heat<br>
      <span style="color:#6B6B6B">⬤</span> No mapped hazard<br>
      <hr style="margin:4px 0;border-color:#eee">
      <span style="opacity:0.5">●</span> Small = few clients<br>
      <span style="font-size:13px;opacity:0.5">●</span> Large = many clients
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=560, returned_objects=[])

# ── Right sidebar: stats ──────────────────────────────────────────────────────
with stat_col:
    st.markdown('<div class="section-head">High-risk zip codes</div>', unsafe_allow_html=True)

    triple = zip_agg[zip_agg['hazard_count'] == 3].sort_values('client_count', ascending=False)
    if len(triple):
        for _, row in triple.head(6).iterrows():
            st.markdown(f"""<div class="risk-fire">
                <b>{row['Zip_clean']}</b> {row['city']}<br>
                {int(row['client_count'])} clients · {int(row['open_cases'])} open
                </div>""", unsafe_allow_html=True)
    else:
        st.caption("No zip with all 3 hazards in current filter")

    st.markdown('<div class="section-head">🔴 Wildfire risk zips</div>', unsafe_allow_html=True)
    fire_zips = zip_agg[zip_agg['hazard_fire']].sort_values('client_count', ascending=False)
    for _, row in fire_zips.head(5).iterrows():
        st.markdown(f"""<div class="risk-fire">
            <b>{row['Zip_clean']}</b> {row['city']}<br>
            {int(row['client_count'])} clients · {int(row['lives_alone'])} alone
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-head">🔵 Flood risk zips</div>', unsafe_allow_html=True)
    flood_zips = zip_agg[zip_agg['hazard_flood']].sort_values('client_count', ascending=False)
    for _, row in flood_zips.head(5).iterrows():
        st.markdown(f"""<div class="risk-flood">
            <b>{row['Zip_clean']}</b> {row['city']}<br>
            {int(row['client_count'])} clients · {int(row['lives_alone'])} alone
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-head">🟠 Heat risk zips</div>', unsafe_allow_html=True)
    heat_zips = zip_agg[zip_agg['hazard_heat']].sort_values('client_count', ascending=False)
    for _, row in heat_zips.head(5).iterrows():
        st.markdown(f"""<div class="risk-heat">
            <b>{row['Zip_clean']}</b> {row['city']}<br>
            {int(row['client_count'])} clients · {int(row['lives_alone'])} alone
            </div>""", unsafe_allow_html=True)

# ── Bottom row: charts ────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="section-head">Vulnerability breakdown</div>', unsafe_allow_html=True)
    vuln_counts = {}
    for c in vuln_cols:
        col_label = vuln_labels[c]
        n = (df[c] == True).sum() + (df[c] == 1).sum()
        if n > 0:
            vuln_counts[col_label] = int(n)
    vuln_df = pd.DataFrame.from_dict(vuln_counts, orient='index', columns=['Count']).sort_values('Count', ascending=True)
    fig_v = px.bar(vuln_df, x='Count', y=vuln_df.index, orientation='h',
                   color_discrete_sequence=['#2E2E2E'])
    fig_v.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=220,
                        xaxis_title='', yaxis_title='',
                        plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(size=11, color='#4A4A4A'),
                        xaxis=dict(showgrid=True, gridcolor='#EBEBEB'))
    st.plotly_chart(fig_v, use_container_width=True)

with c2:
    st.markdown('<div class="section-head">Hazard exposure by open/closed</div>', unsafe_allow_html=True)
    hazard_status = pd.DataFrame({
        'Hazard': ['Wildfire', 'Flood', 'Heat'],
        'Open': [
            df[df['Open_or_Closed']=='Open']['hazard_fire'].sum(),
            df[df['Open_or_Closed']=='Open']['hazard_flood'].sum(),
            df[df['Open_or_Closed']=='Open']['hazard_heat'].sum(),
        ],
        'Closed': [
            df[df['Open_or_Closed']=='Closed']['hazard_fire'].sum(),
            df[df['Open_or_Closed']=='Closed']['hazard_flood'].sum(),
            df[df['Open_or_Closed']=='Closed']['hazard_heat'].sum(),
        ]
    })
    fig_h = px.bar(hazard_status, x='Hazard', y=['Open','Closed'],
                   barmode='group',
                   color_discrete_map={'Open': '#E24B4A', 'Closed': '#B4B2A9'})
    fig_h.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=220,
                        xaxis_title='', yaxis_title='',
                        plot_bgcolor='white', paper_bgcolor='white',
                        legend=dict(orientation='h', yanchor='bottom', y=1, font=dict(size=10)),
                        font=dict(size=11, color='#4A4A4A'),
                        yaxis=dict(showgrid=True, gridcolor='#EBEBEB'))
    st.plotly_chart(fig_h, use_container_width=True)

with c3:
    st.markdown('<div class="section-head">Living arrangements — hazard zones</div>', unsafe_allow_html=True)
    living_hazard = df.groupby('Living_Arrangements').agg(
        total=('Client_ID','count'),
        in_hazard=('hazard_count', lambda x: (x>0).sum())
    ).reset_index().sort_values('total', ascending=False).head(7)
    living_hazard['pct'] = (living_hazard['in_hazard'] / living_hazard['total'] * 100).round(0)
    living_hazard['label'] = living_hazard['Living_Arrangements'].str[:22]
    fig_l = px.bar(living_hazard, x='pct', y='label', orientation='h',
                   color='pct',
                   color_continuous_scale=['#D3D1C7','#888780','#2E2E2E'],
                   labels={'pct':'% in hazard zone','label':''})
    fig_l.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=220,
                        xaxis_title='% in any hazard zone', yaxis_title='',
                        plot_bgcolor='white', paper_bgcolor='white',
                        coloraxis_showscale=False,
                        font=dict(size=10, color='#4A4A4A'),
                        xaxis=dict(showgrid=True, gridcolor='#EBEBEB'))
    st.plotly_chart(fig_l, use_container_width=True)

# ── Client table ──────────────────────────────────────────────────────────────
with st.expander("📋 Client-level data table (filtered)", expanded=False):
    display_cols = ['Zip_clean','City_clean','Open_or_Closed','lives_alone_flag',
                    'hazard_fire','hazard_flood','hazard_heat','hazard_count','Living_Arrangements']
    avail = [c for c in display_cols if c in df.columns]
    rename_map = {
        'Zip_clean':'Zip','City_clean':'City','Open_or_Closed':'Status',
        'lives_alone_flag':'Lives Alone','hazard_fire':'🔴 Fire',
        'hazard_flood':'🔵 Flood','hazard_heat':'🟠 Heat','hazard_count':'# Hazards',
        'Living_Arrangements':'Living Arrangement'
    }
    st.dataframe(
        df[avail].rename(columns=rename_map).reset_index(drop=True),
        use_container_width=True, height=300
    )
    csv = df[avail].rename(columns=rename_map).to_csv(index=False)
    st.download_button("⬇ Export CSV", csv, "aps_hazard_risk.csv", "text/csv")

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(300)
    st.rerun()
