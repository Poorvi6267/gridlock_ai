import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from datetime import datetime, timedelta
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000"

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="TrafficSense",
    page_icon="🚦",
    layout="wide"
)

st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .big-title  { font-size:42px; font-weight:700; color:#00BFFF; }
    .sub-title  { color:#888; font-size:18px; }
    </style>
""", unsafe_allow_html=True)


# =====================================================
# HELPERS
# =====================================================

def api_get(path, default=None):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return default


def api_post(path, payload, timeout=15):
    return requests.post(f"{API_URL}{path}", json=payload, timeout=timeout).json()


# =====================================================
# LOAD DYNAMIC OPTIONS FROM BACKEND
# =====================================================

@st.cache_data(ttl=60)
def fetch_corridors():
    data = api_get("/corridors")
    if data and "corridors" in data:
        return data["corridors"]           # list of {name, risk_score}
    # fallback
    return [
        {"name": c, "risk_score": 50}
        for c in ["Mysore Road","Old Madras Road","Tumkur Road",
                  "Bellary Road 1","ORR East 2","Bannerghata Road"]
    ]


@st.cache_data(ttl=60)
def fetch_junctions():
    data = api_get("/junctions")
    if data and "junctions" in data:
        return data["junctions"]           # list of {name, latitude, longitude}
    return [
        {"name": "Kengeri",           "latitude": 12.9141, "longitude": 77.4820},
        {"name": "Nagavara Junction", "latitude": 13.0468, "longitude": 77.6195},
        {"name": "Hebbal Junction",   "latitude": 13.0450, "longitude": 77.5970},
        {"name": "Silk Board Junction","latitude":12.9177, "longitude": 77.6228},
    ]


corridors_data = fetch_corridors()
junctions_data = fetch_junctions()

corridor_names = [c["name"] for c in corridors_data]
junction_names = [j["name"] for j in junctions_data]
junction_map   = {j["name"]: (j["latitude"], j["longitude"]) for j in junctions_data}

# =====================================================
# HEADER
# =====================================================

st.markdown("<div class='big-title'>🚦 TrafficSense Command Center</div>",
            unsafe_allow_html=True)
st.markdown("<div class='sub-title'>AI Powered Traffic Operations Platform</div>",
            unsafe_allow_html=True)
st.divider()

# =====================================================
# LIVE KPIs  — from /status endpoint
# =====================================================

status = api_get("/status", default={
    "active_incidents": 0, "critical_incidents": 0,
    "police_deployed": 0,  "diversions_active": 0
})

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Incidents (1h)",  status.get("active_incidents",  0))
c2.metric("Critical Incidents (1h)",status.get("critical_incidents",0))
c3.metric("Police Deployed (1h)",   status.get("police_deployed",   0))
c4.metric("Diversions Active (1h)", status.get("diversions_active", 0))

st.divider()

# =====================================================
# CORRIDOR RISK MAP  — all corridors colour-coded
# =====================================================

st.header("🗺 Bangalore Corridor Risk Map")

# Approximate corridor centroids for visualisation
CORRIDOR_CENTROIDS = {
    "Mysore Road":          (12.9141, 77.4820),
    "Old Madras Road":      (12.9929, 77.6678),
    "Tumkur Road":          (13.0274, 77.5388),
    "Bellary Road 1":       (13.0630, 77.5916),
    "Bellary Road 2":       (13.0850, 77.5980),
    "ORR East 1":           (12.9592, 77.6974),
    "ORR East 2":           (12.9300, 77.6850),
    "ORR North 1":          (13.0600, 77.6350),
    "ORR North 2":          (13.0700, 77.5600),
    "Bannerghata Road":     (12.8700, 77.5970),
    "Hosur Road":           (12.8900, 77.6350),
    "CBD 1":                (12.9750, 77.5700),
    "CBD 2":                (12.9800, 77.5750),
    "Hennur Main Road":     (13.0350, 77.6380),
    "Magadi Road":          (12.9700, 77.5050),
    "West of Chord Road":   (13.0000, 77.5380),
    "IRR(Thanisandra road)":(13.0500, 77.6550),
    "ORR West 1":           (12.9900, 77.4800),
    "Airport New South Road":(13.1800,77.6300),
    "Old Airport Road":     (12.9500, 77.6600),
    "Varthur Road":         (12.9300, 77.7200),
    "Non-corridor":         (12.9716, 77.5946),
}

corr_map = folium.Map(location=[12.97, 77.59], zoom_start=11)

for c in corridors_data:
    name  = c["name"]
    score = c["risk_score"]
    if name not in CORRIDOR_CENTROIDS:
        continue
    lat, lon = CORRIDOR_CENTROIDS[name]
    # colour: green (low) → orange → red (high)
    if score >= 60:
        colour = "red"
    elif score >= 30:
        colour = "orange"
    else:
        colour = "green"
    folium.CircleMarker(
        location=[lat, lon],
        radius=8 + score / 10,
        color=colour,
        fill=True,
        fill_opacity=0.7,
        popup=f"{name}\nRisk: {score:.1f}/100",
        tooltip=f"{name}: {score:.1f}"
    ).add_to(corr_map)

st_folium(corr_map, width=1200, height=450)

st.divider()

# =====================================================
# SIDEBAR — INCIDENT SETUP
# =====================================================

with st.sidebar:

    st.header("🚨 Incident Setup")

    event_type = st.selectbox("Incident Type", ["planned", "unplanned"])

    event_cause = st.selectbox(
        "Event Cause",
        ["accident", "construction", "event", "breakdown", "flooding", "protest"]
    )

    corridor_name = st.selectbox("Corridor", corridor_names)

    junction_name = st.selectbox("Junction", junction_names)

    zone_name = st.selectbox("Zone", ["South Zone 1", "Central Zone 1", "East Zone 1"])

    severity = st.selectbox("Severity", ["Low", "Medium", "High"])

    vehicle_count = st.slider("Vehicle Count", 0, 10000, 1500)

    crowd_size = st.slider("Crowd Size", 0, 50000, 5000)

    # Real time from system clock
    now     = datetime.now()
    hour    = st.slider("Hour", 0, 23, now.hour)
    weekday = now.weekday()   # 0=Monday … 6=Sunday (auto, not shown)
    month   = now.month       # auto, not shown

    analyze = st.button("🚀 Analyze Incident", use_container_width=True)

    st.caption(f"📅 {now.strftime('%A, %d %b %Y')}  •  weekday={weekday}, month={month}")

# =====================================================
# PAYLOAD CONSTRUCTION
# =====================================================

severity_map = {"Low": 10, "Medium": 50, "High": 90}

# Real junction coordinates
jlat, jlon = junction_map.get(junction_name, (12.9716, 77.5946))

weekend   = 1 if weekday >= 5 else 0
peak_hour = 1 if hour in [8, 9, 10, 17, 18, 19, 20] else 0

# =====================================================
# SESSION STATE — persist results across re-renders
# =====================================================

for _key in ("ts_result", "ts_rec", "ts_diversion", "ts_payload",
             "ts_junction", "ts_corridor", "ts_event_cause"):
    if _key not in st.session_state:
        st.session_state[_key] = None

if analyze:

    result    = {}
    rec       = {}
    diversion = {}

    payload = {
        "event_type":   event_type,
        "event_cause":  event_cause,          # ← user-chosen, not hardcoded
        "veh_type":     "car",
        "corridor":     corridor_name,
        "zone":         zone_name,
        "junction":     junction_name,
        "latitude":     jlat,                 # ← real junction lat
        "longitude":    jlon,                 # ← real junction lon
        "hour":         hour,
        "weekday":      weekday,              # ← real weekday
        "month":        month,               # ← real month
        "weekend":      weekend,
        "peak_hour":    peak_hour,
        "event_frequency_score": max(1, crowd_size // 2000),
        "closure_risk":          severity_map[severity],
        "duration_risk":         severity_map[severity],
        "junction_count":        max(1, vehicle_count // 200),
        "junction_duration":     max(5, vehicle_count // 50),
        "corridor_count":        max(1, vehicle_count // 100),
        "corridor_duration":     max(5, vehicle_count // 30),
        "historical_impact":     severity_map[severity],
    }

    try:
        result = api_post("/predict", payload)

        if "traffic_impact_index" not in result:
            st.error(f"Prediction error: {result}")
            st.stop()

        rec = api_post("/recommend", {
            "event_type": event_type,
            "corridor":   corridor_name,
            "junction":   junction_name,
            "tii":        result["traffic_impact_index"]
        })

        if "resources" not in rec:
            st.error(f"Recommendation error: {rec}")
            st.stop()

        # ── Persist everything to session_state ──────────────
        st.session_state["ts_result"]      = result
        st.session_state["ts_rec"]         = rec
        st.session_state["ts_diversion"]   = rec.get("diversion", {})
        st.session_state["ts_payload"]     = payload
        st.session_state["ts_junction"]    = junction_name
        st.session_state["ts_corridor"]    = corridor_name
        st.session_state["ts_event_cause"] = event_cause

    except requests.exceptions.Timeout:
        st.error("⏱ Request timed out. Is the backend running? Try: python backend/app.py")
        st.stop()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()

# =====================================================
# RESULTS — rendered from session_state so they
# survive every subsequent Streamlit re-render
# =====================================================

if st.session_state["ts_result"] is None:
    st.stop()

result        = st.session_state["ts_result"]
rec           = st.session_state["ts_rec"]
diversion     = st.session_state["ts_diversion"]
payload       = st.session_state["ts_payload"]
junction_name = st.session_state["ts_junction"]    or junction_name
corridor_name = st.session_state["ts_corridor"]    or corridor_name
event_cause   = st.session_state["ts_event_cause"] or event_cause

st.success("✅ Analysis Complete")

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

st.header("🚨 Executive Summary")
st.info(f"""
**Priority:** {rec['priority']}

**Expected Clearance:** {rec.get('estimated_clearance', 'N/A')}

**Recommended Action:** {rec.get('strategy', 'N/A')}
""")

# =====================================================
# TII GAUGE
# =====================================================

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=result["traffic_impact_index"],
    title={"text": "Traffic Impact Index"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar":  {"color": "#00BFFF"},
        "steps": [
            {"range": [0,  50],  "color": "#1a1a2e"},
            {"range": [50, 75],  "color": "#16213e"},
            {"range": [75, 100], "color": "#0f3460"}
        ]
    }
))
st.plotly_chart(gauge, use_container_width=True)

# =====================================================
# RESOURCE DEPLOYMENT
# =====================================================

st.header("🚓 Resource Deployment")
resources = rec["resources"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Police",     resources["traffic_police"])
c2.metric("Barricades", resources["barricades"])
c3.metric("Tow Trucks", resources["tow_trucks"])
c4.metric("Ambulances", resources["ambulances"])

# =====================================================
# DIVERSION STRATEGY
# =====================================================

st.header("🚧 Diversion Strategy")
if diversion.get("activate"):
    st.success(diversion["level"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Recommended Route", diversion["recommended_route"])
        st.metric("Time Saving",        diversion["expected_time_saving"])
    with c2:
        st.metric("Congestion Reduction", diversion["expected_congestion_reduction"])
    st.write(diversion["strategy"])
else:
    st.info(diversion.get("message", "No diversion required."))

# =====================================================
# ROUTE INTELLIGENCE
# =====================================================

st.divider()
st.header("🗺 Incident Route")

try:
    route_response = api_post("/route", {
        "start_location": f"{junction_name}, Bangalore, India",
        "end_location":   "Majestic, Bangalore, India"
    })
except Exception:
    route_response = {}

coords = route_response.get("coordinates", [])

if coords and len(coords) >= 2:
    route_map = folium.Map(location=coords[0], zoom_start=12)
    folium.PolyLine(coords, weight=6, color="red").add_to(route_map)
    folium.Marker(coords[0],  popup="Incident Location").add_to(route_map)
    folium.Marker(coords[-1], popup="Diversion Destination").add_to(route_map)
    st_folium(route_map, width=1200, height=550)
else:
    st.warning("Route information unavailable.")

# =====================================================
# IMPACT INTELLIGENCE
# =====================================================

st.divider()
st.header("📊 Impact Intelligence")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Traffic Impact Index",  round(result["traffic_impact_index"], 2))
c2.metric("Closure Probability",   f"{result['road_closure_probability']*100:.1f}%")
c3.metric("Duration",              f"{result['predicted_duration_minutes']:.0f} min")
c4.metric("Risk Score",            round(rec["risk_score"], 2))

# =====================================================
# AI REASONING  (SHAP or rule-based)
# =====================================================

st.divider()
st.header("🤖 AI Reasoning")
reasons = result.get("explanation", [])
if reasons:
    for reason in reasons:
        st.success(reason)
else:
    st.info("No explanation available.")

# =====================================================
# SMART ALERTS
# =====================================================

st.divider()
st.header("🚨 Smart Alerts")
alerts_fired = False
if result["road_closure_probability"] > 0.8:
    st.error("High probability of road closure.")
    alerts_fired = True
if result["traffic_impact_index"] > 80:
    st.error("Severe congestion predicted.")
    alerts_fired = True
if result["predicted_duration_minutes"] > 180:
    st.warning("Extended disruption expected.")
    alerts_fired = True
if not alerts_fired:
    st.success("No critical alerts.")

# =====================================================
# RESOURCE OPTIMIZATION
# =====================================================

st.divider()
st.header("🎯 Resource Optimization")
if rec["risk_score"] > 80:
    st.error(f"Deploy maximum field resources immediately. {rec.get('strategy','')}")
elif rec["risk_score"] > 60:
    st.warning(f"Deploy moderate resources and monitor. {rec.get('strategy','')}")
else:
    st.success(f"Routine deployment sufficient. {rec.get('strategy','')}")

# =====================================================
# CORRIDOR RISK RANKING  — live from /corridors
# =====================================================

st.divider()
st.header("📈 Corridor Risk Ranking")

risk_df = pd.DataFrame(corridors_data).rename(
    columns={"name": "Corridor", "risk_score": "Risk"}
).set_index("Corridor").sort_values("Risk", ascending=True)

# Highlight the selected corridor
colours = [
    "#00BFFF" if c == corridor_name else "#444466"
    for c in risk_df.index
]

fig_bar = go.Figure(go.Bar(
    x=risk_df["Risk"],
    y=risk_df.index,
    orientation="h",
    marker_color=colours,
))
fig_bar.update_layout(
    height=max(300, len(risk_df) * 22),
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis_title="Normalised Risk (0–100)",
)
st.plotly_chart(fig_bar, use_container_width=True)

# =====================================================
# HISTORICAL COMPARISON  — from /history
# =====================================================

st.divider()
st.header("📉 Historical Comparison")

history_data = api_get("/history", default={})
hist_avg     = history_data.get("average_duration_minutes")
total_preds  = history_data.get("total_predictions", 0)

if hist_avg is not None:
    label = f"Historical Avg ({total_preds} runs)"
else:
    hist_avg = 95   # fallback sentinel
    label    = "Historical Avg (no data yet)"

history = pd.DataFrame({
    "Scenario": [label, "Current Incident"],
    "Duration": [hist_avg, result["predicted_duration_minutes"]]
})
st.bar_chart(history.set_index("Scenario"))

# =====================================================
# INCIDENT LIFECYCLE
# =====================================================

st.divider()
st.header("🕒 Incident Lifecycle")
st.markdown("""
✅ Incident Reported ↓
🤖 AI Impact Assessment ↓
🚓 Resource Deployment ↓
🚧 Diversion Planning ↓
🟢 Expected Resolution
""")

# =====================================================
# INCIDENT REPORT DOWNLOAD
# =====================================================

report = f"""TRAFFICSENSE INCIDENT REPORT

Location:    {junction_name}  ({jlat:.4f}, {jlon:.4f})
Corridor:    {corridor_name}
Event Type:  {event_type}
Event Cause: {event_cause}
Priority:    {rec['priority']}

Traffic Impact Index:  {result['traffic_impact_index']}
Closure Probability:   {result['road_closure_probability']}
Predicted Duration:    {result['predicted_duration_minutes']} min

Risk Score:            {rec['risk_score']}
Clearance Estimate:    {rec.get('estimated_clearance', 'N/A')}

Recommended Action:
{rec.get('strategy', 'N/A')}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

st.download_button(
    "📄 Download Incident Report",
    report,
    file_name="TrafficSense_Report.txt"
)

# =====================================================
# SCENARIO SIMULATOR  — live /predict call
# =====================================================

st.divider()
st.header("🧪 Scenario Simulator")
st.caption("Calls /predict with the adjusted parameters — not an estimate.")

sim_vehicle_count = st.slider(
    "Simulated Vehicle Count", 0, 15000, vehicle_count, key="sim_vehicle"
)
sim_severity = st.selectbox(
    "Simulated Severity", ["Low", "Medium", "High"], key="sim_severity"
)
sim_hour = st.slider("Simulated Hour", 0, 23, hour, key="sim_hour")

if st.button("▶ Run Simulation"):
    sim_peak = 1 if sim_hour in [8, 9, 10, 17, 18, 19, 20] else 0
    sim_payload = {**payload,
        "hour":             sim_hour,
        "peak_hour":        sim_peak,
        "closure_risk":     severity_map[sim_severity],
        "duration_risk":    severity_map[sim_severity],
        "historical_impact":severity_map[sim_severity],
        "junction_count":   max(1, sim_vehicle_count // 200),
        "junction_duration":max(5, sim_vehicle_count // 50),
        "corridor_count":   max(1, sim_vehicle_count // 100),
        "corridor_duration":max(5, sim_vehicle_count // 30),
    }
    try:
        sim_result = api_post("/predict", sim_payload)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Simulated TII",
                   round(sim_result.get("traffic_impact_index", 0), 2),
                   delta=round(sim_result.get("traffic_impact_index",0)
                               - result["traffic_impact_index"], 2))
        sc2.metric("Simulated Duration",
                   f"{sim_result.get('predicted_duration_minutes',0):.0f} min",
                   delta=f"{sim_result.get('predicted_duration_minutes',0)
                            - result['predicted_duration_minutes']:+.0f} min")
        sc3.metric("Closure Probability",
                   f"{sim_result.get('road_closure_probability',0)*100:.1f}%")
    except Exception as e:
        st.error(f"Simulation error: {e}")

# =====================================================
# COMMAND RECOMMENDATION
# =====================================================

st.divider()
st.header("📋 Recommended Command Action")

diversion_active = diversion.get("activate", False)
command_text = f"""
Priority Level: {rec['priority']}

Recommended Route:
{diversion.get('recommended_route', 'N/A') if diversion_active else 'No diversion active'}

Expected Clearance:
{rec.get('estimated_clearance', 'N/A')}

Expected Time Saving:
{diversion.get('expected_time_saving', 'N/A') if diversion_active else 'N/A'}
"""
st.code(command_text)

# =====================================================
# INCIDENT CRITICALITY SCORE
# =====================================================

st.divider()
st.header("⚡ Incident Criticality")

criticality = round(
    (result["traffic_impact_index"] + min(rec["risk_score"], 100)) / 2, 2
)
st.metric("Criticality Score", criticality)
st.progress(min(criticality / 100, 1.0))

# =====================================================
# LIVE OPERATIONS FEED
# =====================================================

st.divider()
st.header("📡 Operations Feed")

t    = datetime.now()
feed = pd.DataFrame({
    "Time": [
        (t + timedelta(minutes=i * 7)).strftime("%H:%M")
        for i in range(4)
    ],
    "Event": [
        "Incident Reported",
        "Prediction Generated",
        "Resources Assigned",
        "Diversion Activated"
    ]
})
st.dataframe(feed, use_container_width=True)

# =====================================================
# AI ACTION CENTER
# =====================================================

st.divider()
st.header("🤖 AI Recommended Actions")

actions = []
if result["traffic_impact_index"] > 80:
    actions.append("Activate full diversion plan")
if result["road_closure_probability"] > 0.7:
    actions.append("Prepare road closure resources")
if rec["risk_score"] > 75:
    actions.append("Deploy additional traffic police")
if not actions:
    actions.append("Continue monitoring traffic conditions")
for action in actions:
    st.success(action)

# =====================================================
# RESOURCE UTILIZATION
# =====================================================

st.divider()
st.header("📊 Resource Utilization")

resource_df = pd.DataFrame({
    "Resource": ["Police", "Barricades", "Tow Trucks", "Ambulances"],
    "Units": [
        resources["traffic_police"], resources["barricades"],
        resources["tow_trucks"],     resources["ambulances"]
    ]
})
st.bar_chart(resource_df.set_index("Resource"))

# =====================================================
# DIVERSION EFFECTIVENESS
# =====================================================

st.divider()
st.header("🚧 Diversion Effectiveness")

if diversion.get("activate", False):
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Expected Reduction", diversion["expected_congestion_reduction"])
    with c2:
        st.metric("Expected Time Saving", diversion["expected_time_saving"])
else:
    st.info("No diversion active.")

# =====================================================
# TRAFFICSENSE SCORECARD
# =====================================================

st.divider()
st.header("🏆 TrafficSense Scorecard")

score = round(
    (result["traffic_impact_index"] * 0.5)
    + (min(rec["risk_score"], 100) * 0.5), 2
)
st.metric("TrafficSense Index", score)
st.progress(min(score / 100, 1.0))

# =====================================================
# MODEL CONFIDENCE
# =====================================================

st.divider()
st.header("🎯 Prediction Confidence")
st.caption("Heuristic — higher confidence near mid-range TII values where training data is densest.")

confidence = max(
    70,
    min(98, int(100 - abs(result["traffic_impact_index"] - 50) / 2))
)
st.metric("Confidence", f"{confidence}%")
