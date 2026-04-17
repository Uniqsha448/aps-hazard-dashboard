import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="APS Disaster Risk Dashboard | Alameda County SSA",
    page_icon="🚨",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  h1,h2,h3 { font-family: 'IBM Plex Mono', monospace; }
  .metric-box {
    background: #0f1923;
    border: 1px solid #2a3f52;
    border-radius: 8px;
    padding: 18px 22px;
    text-align: center;
  }
  .metric-box .label { color: #7a9bb5; font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
  .metric-box .value { color: #f0f4f8; font-size: 32px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }
  .metric-box .sub   { color: #c0d8eb; font-size: 13px; margin-top: 4px; }
  .alert-banner {
    border-radius: 8px;
    padding: 14px 20px;
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 16px;
    border-left: 5px solid;
  }
  .alert-wildfire { background:#2d1200; border-color:#ff6b1a; color:#ffaa77; }
  .alert-flood    { background:#001a2d; border-color:#1a8cff; color:#77bbff; }
  .alert-heat     { background:#2d2200; border-color:#ffcc00; color:#ffe680; }
  .alert-multi    { background:#2d001a; border-color:#ff1a6b; color:#ff77bb; }
  .sidebar-header { font-family:'IBM Plex Mono',monospace; font-size:13px; letter-spacing:1px; color:#7a9bb5; margin-top:12px; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ── Real SSA Data ─────────────────────────────────────────────────────────────
RAW = [
  {"quintile":1,"zip":94541,"city":"HAYWARD","no_mlv":189,"yes_mlv":510,"sum_mlv":1173},
  {"quintile":1,"zip":94501,"city":"ALAMEDA","no_mlv":200,"yes_mlv":450,"sum_mlv":1082},
  {"quintile":1,"zip":94568,"city":"DUBLIN","no_mlv":228,"yes_mlv":409,"sum_mlv":897},
  {"quintile":1,"zip":94605,"city":"OAKLAND","no_mlv":187,"yes_mlv":369,"sum_mlv":882},
  {"quintile":1,"zip":94621,"city":"OAKLAND","no_mlv":92,"yes_mlv":348,"sum_mlv":863},
  {"quintile":1,"zip":94544,"city":"HAYWARD","no_mlv":184,"yes_mlv":361,"sum_mlv":840},
  {"quintile":1,"zip":94577,"city":"SAN LEANDRO","no_mlv":124,"yes_mlv":360,"sum_mlv":840},
  {"quintile":1,"zip":94550,"city":"LIVERMORE","no_mlv":152,"yes_mlv":283,"sum_mlv":693},
  {"quintile":1,"zip":94608,"city":"EMERYVILLE","no_mlv":102,"yes_mlv":285,"sum_mlv":674},
  {"quintile":1,"zip":94601,"city":"OAKLAND","no_mlv":117,"yes_mlv":279,"sum_mlv":669},
  {"quintile":1,"zip":94546,"city":"CASTRO VALLEY","no_mlv":137,"yes_mlv":266,"sum_mlv":648},
  {"quintile":2,"zip":94603,"city":"OAKLAND","no_mlv":96,"yes_mlv":285,"sum_mlv":642},
  {"quintile":2,"zip":94612,"city":"OAKLAND","no_mlv":68,"yes_mlv":257,"sum_mlv":601},
  {"quintile":2,"zip":94578,"city":"SAN LEANDRO","no_mlv":98,"yes_mlv":264,"sum_mlv":598},
  {"quintile":2,"zip":94587,"city":"UNION CITY","no_mlv":168,"yes_mlv":249,"sum_mlv":579},
  {"quintile":2,"zip":94606,"city":"OAKLAND","no_mlv":85,"yes_mlv":248,"sum_mlv":575},
  {"quintile":2,"zip":94538,"city":"FREMONT","no_mlv":99,"yes_mlv":249,"sum_mlv":566},
  {"quintile":2,"zip":94703,"city":"BERKELEY","no_mlv":81,"yes_mlv":225,"sum_mlv":532},
  {"quintile":2,"zip":94702,"city":"BERKELEY","no_mlv":95,"yes_mlv":227,"sum_mlv":516},
  {"quintile":2,"zip":94611,"city":"OAKLAND","no_mlv":137,"yes_mlv":207,"sum_mlv":510},
  {"quintile":2,"zip":94607,"city":"OAKLAND","no_mlv":74,"yes_mlv":211,"sum_mlv":474},
  {"quintile":2,"zip":94602,"city":"OAKLAND","no_mlv":109,"yes_mlv":199,"sum_mlv":458},
  {"quintile":3,"zip":94560,"city":"NEWARK","no_mlv":107,"yes_mlv":180,"sum_mlv":429},
  {"quintile":3,"zip":94545,"city":"HAYWARD","no_mlv":95,"yes_mlv":195,"sum_mlv":425},
  {"quintile":3,"zip":94551,"city":"LIVERMORE","no_mlv":109,"yes_mlv":188,"sum_mlv":408},
  {"quintile":3,"zip":94566,"city":"PLEASANTON","no_mlv":133,"yes_mlv":166,"sum_mlv":388},
  {"quintile":3,"zip":94609,"city":"OAKLAND","no_mlv":70,"yes_mlv":163,"sum_mlv":386},
  {"quintile":3,"zip":94619,"city":"OAKLAND","no_mlv":76,"yes_mlv":159,"sum_mlv":375},
  {"quintile":3,"zip":94610,"city":"OAKLAND","no_mlv":69,"yes_mlv":141,"sum_mlv":327},
  {"quintile":3,"zip":94704,"city":"BERKELEY","no_mlv":46,"yes_mlv":132,"sum_mlv":313},
  {"quintile":3,"zip":94580,"city":"SAN LORENZO","no_mlv":64,"yes_mlv":131,"sum_mlv":305},
  {"quintile":3,"zip":94588,"city":"PLEASANTON","no_mlv":84,"yes_mlv":102,"sum_mlv":234},
  {"quintile":3,"zip":94709,"city":"BERKELEY","no_mlv":42,"yes_mlv":91,"sum_mlv":227},
  {"quintile":4,"zip":94579,"city":"SAN LEANDRO","no_mlv":46,"yes_mlv":96,"sum_mlv":223},
  {"quintile":4,"zip":94705,"city":"BERKELEY","no_mlv":58,"yes_mlv":87,"sum_mlv":209},
  {"quintile":4,"zip":94618,"city":"OAKLAND","no_mlv":64,"yes_mlv":91,"sum_mlv":206},
  {"quintile":4,"zip":94539,"city":"FREMONT","no_mlv":122,"yes_mlv":87,"sum_mlv":180},
  {"quintile":4,"zip":94710,"city":"BERKELEY","no_mlv":30,"yes_mlv":75,"sum_mlv":162},
  {"quintile":4,"zip":94706,"city":"ALBANY","no_mlv":42,"yes_mlv":66,"sum_mlv":151},
  {"quintile":4,"zip":94708,"city":"BERKELEY","no_mlv":51,"yes_mlv":61,"sum_mlv":150},
  {"quintile":4,"zip":94707,"city":"BERKELEY","no_mlv":49,"yes_mlv":63,"sum_mlv":143},
  {"quintile":4,"zip":94555,"city":"FREMONT","no_mlv":71,"yes_mlv":53,"sum_mlv":124},
  {"quintile":4,"zip":94502,"city":"ALAMEDA","no_mlv":40,"yes_mlv":46,"sum_mlv":100},
  {"quintile":4,"zip":94542,"city":"HAYWARD","no_mlv":32,"yes_mlv":37,"sum_mlv":84},
  {"quintile":5,"zip":94552,"city":"CASTRO VALLEY","no_mlv":33,"yes_mlv":34,"sum_mlv":70},
  {"quintile":5,"zip":94604,"city":"OAKLAND","no_mlv":0,"yes_mlv":7,"sum_mlv":14},
  {"quintile":5,"zip":94701,"city":"BERKELEY","no_mlv":0,"yes_mlv":4,"sum_mlv":13},
  {"quintile":5,"zip":94557,"city":"HAYWARD","no_mlv":0,"yes_mlv":3,"sum_mlv":4},
  {"quintile":5,"zip":94620,"city":"PIEDMONT","no_mlv":0,"yes_mlv":1,"sum_mlv":3},
  {"quintile":5,"zip":94712,"city":"BERKELEY","no_mlv":1,"yes_mlv":1,"sum_mlv":3},
  {"quintile":5,"zip":94536,"city":"FREMONT","no_mlv":1,"yes_mlv":0,"sum_mlv":0},
  {"quintile":5,"zip":94613,"city":"OAKLAND","no_mlv":2,"yes_mlv":0,"sum_mlv":0},
  {"quintile":5,"zip":94623,"city":"OAKLAND","no_mlv":1,"yes_mlv":0,"sum_mlv":0},
]

# Hazard zone assignments based on Alameda County EOP / CalFire / FEMA data
HAZARD_ZONES = {
    # Wildfire (WUI zones — Oakland Hills, Hayward Hills, Castro Valley, Livermore, Dublin)
    "wildfire": [94546, 94619, 94611, 94618, 94705, 94708, 94709, 94704,
                 94568, 94550, 94551, 94552, 94545, 94542, 94588, 94566],
    # Flood (Bay shoreline, Alameda Island, Newark, Hayward, Union City)
    "flood":    [94501, 94502, 94560, 94587, 94544, 94541, 94577, 94578,
                 94580, 94555, 94538, 94539],
    # Extreme Heat (Inland valleys — Livermore, Pleasanton, Dublin, parts of Fremont)
    "heat":     [94550, 94551, 94568, 94566, 94588, 94536, 94537, 94539,
                 94555, 94538],
}

SCENARIO_CONFIG = {
    "🔥 Wildfire": {
        "key": "wildfire",
        "color": "#ff6b1a",
        "bg": "#2d1200",
        "text_color": "#ffaa77",
        "alert_class": "alert-wildfire",
        "icon": "🔥",
        "desc": "WUI fire threat zones based on CAL FIRE FHSZ data — Oakland Hills, Hayward Hills, Castro Valley, Livermore, Dublin"
    },
    "🌊 Flood": {
        "key": "flood",
        "color": "#1a8cff",
        "bg": "#001a2d",
        "text_color": "#77bbff",
        "alert_class": "alert-flood",
        "icon": "🌊",
        "desc": "FEMA 100-year flood zones — Alameda Island, Hayward Bay shoreline, Newark, Union City, San Leandro"
    },
    "🌡️ Extreme Heat": {
        "key": "heat",
        "color": "#ffcc00",
        "bg": "#2d2200",
        "text_color": "#ffe680",
        "alert_class": "alert-heat",
        "icon": "🌡️",
        "desc": "Inland valley heat corridors — Livermore Valley, Pleasanton-Dublin, Fremont"
    },
    "⚠️ Multi-Hazard (All)": {
        "key": "multi",
        "color": "#ff1a6b",
        "bg": "#2d001a",
        "text_color": "#ff77bb",
        "alert_class": "alert-multi",
        "icon": "⚠️",
        "desc": "All three hazard zones combined — clients exposed to at least one hazard type"
    },
}

# ZIP → lat/lon lookup (approximate centroids)
ZIP_COORDS = {
    94541: (37.668, -122.081), 94501: (37.765, -122.243), 94568: (37.702, -121.936),
    94605: (37.747, -122.160), 94621: (37.742, -122.185), 94544: (37.634, -122.059),
    94577: (37.723, -122.157), 94550: (37.682, -121.768), 94608: (37.837, -122.283),
    94601: (37.769, -122.221), 94546: (37.695, -122.062), 94603: (37.736, -122.175),
    94612: (37.812, -122.268), 94578: (37.706, -122.143), 94587: (37.591, -122.016),
    94606: (37.787, -122.237), 94538: (37.550, -121.983), 94703: (37.858, -122.278),
    94702: (37.863, -122.290), 94611: (37.820, -122.222), 94607: (37.802, -122.291),
    94602: (37.802, -122.215), 94560: (37.530, -122.040), 94545: (37.617, -122.059),
    94551: (37.695, -121.736), 94566: (37.662, -121.874), 94609: (37.841, -122.258),
    94619: (37.787, -122.188), 94610: (37.813, -122.239), 94704: (37.867, -122.261),
    94580: (37.680, -122.121), 94588: (37.694, -121.874), 94709: (37.879, -122.269),
    94579: (37.692, -122.149), 94705: (37.854, -122.251), 94618: (37.836, -122.234),
    94539: (37.510, -121.939), 94710: (37.872, -122.301), 94706: (37.886, -122.302),
    94708: (37.893, -122.271), 94707: (37.890, -122.285), 94555: (37.553, -122.043),
    94502: (37.745, -122.228), 94542: (37.651, -122.035), 94552: (37.688, -122.040),
    94604: (37.812, -122.268), 94701: (37.870, -122.302), 94557: (37.668, -122.081),
    94620: (37.824, -122.232), 94712: (37.870, -122.302), 94536: (37.549, -121.984),
    94613: (37.790, -122.196), 94623: (37.811, -122.297),
}

# ── Build DataFrame ───────────────────────────────────────────────────────────
df = pd.DataFrame(RAW)
df["total_clients"] = df["no_mlv"] + df["yes_mlv"]
df["mlv_pct"] = (df["yes_mlv"] / df["total_clients"] * 100).round(1)
df["lat"] = df["zip"].map(lambda z: ZIP_COORDS.get(z, (37.7, -122.1))[0])
df["lon"] = df["zip"].map(lambda z: ZIP_COORDS.get(z, (37.7, -122.1))[1])
df["zip_str"] = df["zip"].astype(str)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚨 APS Risk Dashboard")
    st.markdown("**Alameda County Social Services Agency**")
    st.markdown("---")

    st.markdown('<p class="sidebar-header">DISASTER SCENARIO</p>', unsafe_allow_html=True)
    scenario = st.selectbox(
        "Select scenario to activate:",
        list(SCENARIO_CONFIG.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown('<p class="sidebar-header">VULNERABILITY FILTER</p>', unsafe_allow_html=True)
    quintile_filter = st.multiselect(
        "Show quintiles:",
        [1, 2, 3, 4, 5],
        default=[1, 2, 3],
        format_func=lambda x: f"Q{x} — {'Highest' if x==1 else 'High' if x==2 else 'Medium' if x==3 else 'Low' if x==4 else 'Lowest'} Risk",
        label_visibility="collapsed"
    )

    st.markdown('<p class="sidebar-header">CITY FILTER</p>', unsafe_allow_html=True)
    cities = sorted(df["city"].unique())
    city_filter = st.multiselect("Cities:", cities, default=[], label_visibility="collapsed", placeholder="All cities")

    st.markdown("---")
    st.caption("Data: APS Vulnerabilities Report\nCases received 1/1/2023–3/31/2026\nN = 13,364 clients | 55 ZIP codes")

# ── Apply Hazard Zone Logic ───────────────────────────────────────────────────
cfg = SCENARIO_CONFIG[scenario]

if cfg["key"] == "multi":
    all_hazard_zips = set()
    for v in HAZARD_ZONES.values():
        all_hazard_zips.update(v)
    df["in_hazard_zone"] = df["zip"].isin(all_hazard_zips)
else:
    hazard_zips = set(HAZARD_ZONES[cfg["key"]])
    df["in_hazard_zone"] = df["zip"].isin(hazard_zips)

# Apply filters
filtered = df.copy()
if quintile_filter:
    filtered = filtered[filtered["quintile"].isin(quintile_filter)]
if city_filter:
    filtered = filtered[filtered["city"].isin(city_filter)]

at_risk = filtered[filtered["in_hazard_zone"]]
not_at_risk = filtered[~filtered["in_hazard_zone"]]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"# APS Disaster Risk Intelligence Dashboard")
st.markdown(f"**Alameda County SSA · Adult Protective Services · Emergency Preparedness Planning**")

# Alert banner
alert_msg = f"{cfg['icon']} <strong>ACTIVE SCENARIO: {scenario.upper()}</strong> — {cfg['desc']}"
st.markdown(f'<div class="alert-banner {cfg["alert_class"]}">{alert_msg}</div>', unsafe_allow_html=True)

# ── METRICS ROW ───────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_clients_shown = filtered["total_clients"].sum()
clients_at_risk = at_risk["total_clients"].sum()
mlv_at_risk = at_risk["yes_mlv"].sum()
zips_at_risk = len(at_risk)
pct_at_risk = round(clients_at_risk / total_clients_shown * 100, 1) if total_clients_shown > 0 else 0

with col1:
    st.markdown(f'<div class="metric-box"><div class="label">Total Clients (filtered)</div><div class="value">{total_clients_shown:,}</div><div class="sub">across {len(filtered)} ZIP codes</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><div class="label">{cfg["icon"]} At-Risk Clients</div><div class="value" style="color:{cfg["color"]}">{clients_at_risk:,}</div><div class="sub">{pct_at_risk}% of filtered total</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><div class="label">MLV Clients in Hazard Zone</div><div class="value" style="color:{cfg["color"]}">{mlv_at_risk:,}</div><div class="sub">mobility-limited + at risk</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-box"><div class="label">ZIPs in Hazard Zone</div><div class="value">{zips_at_risk}</div><div class="sub">of {len(filtered)} shown</div></div>', unsafe_allow_html=True)
with col5:
    vehicles_needed = -(-mlv_at_risk // 4)  # ceiling division, 4 per vehicle
    st.markdown(f'<div class="metric-box"><div class="label">Est. Vehicles Needed</div><div class="value">{vehicles_needed:,}</div><div class="sub">for MLV evacuation (4/vehicle)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAP + TABLE ───────────────────────────────────────────────────────────────
map_col, table_col = st.columns([3, 2])

with map_col:
    st.markdown("### 📍 Client Distribution by ZIP Code")
    st.caption("Bubble size = total clients | Red = in hazard zone | Blue = outside hazard zone")

    map_df = filtered.copy()
    map_df["status"] = map_df["in_hazard_zone"].map({True: f"{cfg['icon']} In Hazard Zone", False: "Outside Hazard Zone"})
    map_df["color_val"] = map_df["in_hazard_zone"].map({True: cfg["color"], False: "#3a6ea5"})
    map_df["hover"] = map_df.apply(
        lambda r: f"ZIP {r['zip']} — {r['city']}<br>Total clients: {r['total_clients']:,}<br>MLV clients: {r['yes_mlv']:,} ({r['mlv_pct']}%)<br>MLV burden score: {r['sum_mlv']:,}<br>Quintile: Q{r['quintile']}",
        axis=1
    )

    fig_map = go.Figure()

    for in_zone, group_df in map_df.groupby("in_hazard_zone"):
        color = cfg["color"] if in_zone else "#3a6ea5"
        name = f"{cfg['icon']} Hazard Zone" if in_zone else "Safe Zone"
        fig_map.add_trace(go.Scattermapbox(
            lat=group_df["lat"],
            lon=group_df["lon"],
            mode="markers",
            marker=dict(
                size=group_df["total_clients"] / 12,
                color=color,
                opacity=0.8,
                sizemin=6,
            ),
            text=group_df["hover"],
            hovertemplate="%{text}<extra></extra>",
            name=name
        ))

    fig_map.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=37.73, lon=-122.13), zoom=9.5),
        margin=dict(l=0, r=0, t=0, b=0),
        height=430,
        legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_map, use_container_width=True)

with table_col:
    st.markdown("### 🔴 Highest-Risk ZIPs")
    st.caption(f"Sorted by MLV clients in {scenario} zone")

    if len(at_risk) > 0:
        display_df = at_risk[["zip_str", "city", "quintile", "total_clients", "yes_mlv", "mlv_pct", "sum_mlv"]].copy()
        display_df.columns = ["ZIP", "City", "Q", "Total", "MLV Clients", "MLV%", "Burden Score"]
        display_df = display_df.sort_values("MLV Clients", ascending=False).head(15)
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True,
        )
    else:
        st.info("No ZIPs in hazard zone for current filters.")

# ── CHARTS ROW ───────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### MLV Burden by Quintile")
    q_summary = filtered.groupby("quintile").agg(
        yes_mlv=("yes_mlv", "sum"),
        no_mlv=("no_mlv", "sum"),
        sum_mlv=("sum_mlv", "sum"),
        in_hazard=("in_hazard_zone", "sum")
    ).reset_index()
    q_summary["total"] = q_summary["yes_mlv"] + q_summary["no_mlv"]
    fig1 = go.Figure()
    fig1.add_bar(x=q_summary["quintile"].astype(str), y=q_summary["no_mlv"], name="No MLV", marker_color="#2a4a6b")
    fig1.add_bar(x=q_summary["quintile"].astype(str), y=q_summary["yes_mlv"], name="Has MLV", marker_color=cfg["color"])
    fig1.update_layout(
        barmode="stack", height=280, margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c0d8eb"), legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Quintile", gridcolor="#1a2d3f"),
        yaxis=dict(title="Clients", gridcolor="#1a2d3f")
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("#### Hazard Exposure: MLV vs Non-MLV")
    in_z = at_risk[["yes_mlv","no_mlv"]].sum()
    out_z = not_at_risk[["yes_mlv","no_mlv"]].sum()
    fig2 = go.Figure(data=[
        go.Bar(name="Has MLV", x=["In Hazard Zone","Outside Zone"], y=[in_z["yes_mlv"], out_z["yes_mlv"]], marker_color=cfg["color"]),
        go.Bar(name="No MLV",  x=["In Hazard Zone","Outside Zone"], y=[in_z["no_mlv"], out_z["no_mlv"]], marker_color="#2a4a6b"),
    ])
    fig2.update_layout(
        barmode="group", height=280, margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c0d8eb"), legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#1a2d3f"), yaxis=dict(title="Clients", gridcolor="#1a2d3f")
    )
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown("#### Top 8 Cities — MLV Clients at Risk")
    city_risk = at_risk.groupby("city")["yes_mlv"].sum().sort_values(ascending=True).tail(8)
    fig3 = go.Figure(go.Bar(
        x=city_risk.values, y=city_risk.index,
        orientation="h", marker_color=cfg["color"],
    ))
    fig3.update_layout(
        height=280, margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c0d8eb"),
        xaxis=dict(title="MLV Clients", gridcolor="#1a2d3f"),
        yaxis=dict(gridcolor="#1a2d3f")
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── REGISTRY IMPACT ESTIMATOR ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Registry Impact Estimator")
st.caption("Estimate how many clients a proactive evacuation registry would protect — adjust enrollment rate below")

reg_col1, reg_col2 = st.columns([1, 2])

with reg_col1:
    enrollment_rate = st.slider("Estimated registry enrollment rate (%)", 10, 100, 60, 5)
    outreach_hours_per_client = st.slider("Avg. outreach hours per client", 1, 8, 2)

with reg_col2:
    total_mlv_at_risk = at_risk["yes_mlv"].sum()
    registered = int(total_mlv_at_risk * enrollment_rate / 100)
    unregistered = total_mlv_at_risk - registered
    hours_saved = registered * outreach_hours_per_client
    vehicles_reg = -(-registered // 4)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("MLV Clients Registered", f"{registered:,}", f"{enrollment_rate}% enrolled")
    r2.metric("Clients Still Unreached", f"{unregistered:,}", f"{100-enrollment_rate}% gap", delta_color="inverse")
    r3.metric("Staff Hours Saved", f"{hours_saved:,}", "vs. door-to-door")
    r4.metric("Vehicles Pre-Staged", f"{vehicles_reg:,}", "based on registry")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚠️ Hazard zone assignments are based on Alameda County EOP, CAL FIRE FHSZ maps, and FEMA NFHL data. This dashboard uses APS client vulnerability data for emergency planning purposes only. Data source: APS Vulnerabilities Report, cases received 1/1/2023–3/31/2026, N=13,364 clients.")
