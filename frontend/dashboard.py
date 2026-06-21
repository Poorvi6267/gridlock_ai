import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Gridlock AI",
    page_icon="🚦",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title("🚦 Gridlock AI")
st.subheader("Traffic Impact Intelligence Platform")

# =====================================================
# CITY COMMAND CENTER
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Active Incidents", 17)
c2.metric("Critical Incidents", 3)
c3.metric("Police Deployed", 124)
c4.metric("Diversions Active", 8)

st.divider()

# =====================================================
# INCIDENT INFORMATION
# =====================================================

st.header("📍 Incident Information")

event_type = st.selectbox(
    "Event Type",
    ["planned", "unplanned"]
)

corridor_name = st.selectbox(
    "Corridor",
    [
        "Mysore Road",
        "Bellary Road",
        "Outer Ring Road",
        "Bannerghatta Road"
    ]
)

junction_name = st.selectbox(
    "Junction",
    [
        "Kengeri",
        "Nagavara Junction",
        "Hebbal Junction",
        "Silk Board Junction"
    ]
)

zone_name = st.selectbox(
    "Zone",
    [
        "South Zone 1",
        "Central Zone 1",
        "East Zone 1"
    ]
)

# =====================================================
# INCIDENT PARAMETERS
# =====================================================

st.header("🚨 Incident Parameters")

severity = st.selectbox(
    "Severity",
    ["Low", "Medium", "High"]
)

vehicle_count = st.slider(
    "Estimated Vehicle Count",
    0,
    10000,
    1500
)

crowd_size = st.slider(
    "Expected Crowd Size",
    0,
    50000,
    5000
)

hour = st.slider(
    "Hour Of Day",
    0,
    23,
    18
)

severity_map = {
    "Low": 10,
    "Medium": 50,
    "High": 90
}

# =====================================================
# ANALYSIS
# =====================================================

if st.button(
    "🚀 Analyze Incident",
    use_container_width=True
):

    peak_hour = 1 if hour in [8, 9, 10, 17, 18, 19, 20] else 0

    payload = {
        "event_type": event_type,
        "event_cause": "construction",
        "veh_type": "car",
        "corridor": corridor_name,
        "zone": zone_name,
        "junction": junction_name,
        "latitude": 12.97,
        "longitude": 77.59,
        "hour": hour,
        "weekday": 1,
        "month": 6,
        "weekend": 0,
        "peak_hour": peak_hour,
        "event_frequency_score": max(
            1,
            crowd_size // 2000
        ),
        "closure_risk": severity_map[severity],
        "duration_risk": severity_map[severity],
        "junction_count": max(
            1,
            vehicle_count // 200
        ),
        "junction_duration": max(
            5,
            vehicle_count // 50
        ),
        "corridor_count": max(
            1,
            vehicle_count // 100
        ),
        "corridor_duration": max(
            5,
            vehicle_count // 30
        ),
        "historical_impact": severity_map[severity]
    }

    try:

        response = requests.post(
            f"{API_URL}/predict",
            json=payload
        )

        result = response.json()

        if "error" in result:
            st.error(result["error"])
            st.stop()

        recommendation_payload = {
            "event_type": event_type,
            "corridor": corridor_name,
            "junction": junction_name,
            "tii": result["traffic_impact_index"]
        }

        rec = requests.post(
            f"{API_URL}/recommend",
            json=recommendation_payload
        ).json()

        st.success("Analysis Complete")

        # =====================================================
        # COMMAND CENTER
        # =====================================================

        st.divider()
        st.header("🚦 Traffic Command Center")

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=result["traffic_impact_index"],
                title={"text": "Traffic Impact Index"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "steps": [
                        {"range": [0, 40], "color": "green"},
                        {"range": [40, 70], "color": "orange"},
                        {"range": [70, 100], "color": "red"}
                    ]
                }
            )
        )

        st.plotly_chart(
            gauge,
            use_container_width=True
        )

        # =====================================================
        # INCIDENT IMPACT
        # =====================================================

        st.header("📊 Incident Impact")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Traffic Impact Index",
            round(result["traffic_impact_index"], 2)
        )

        c2.metric(
            "Closure Probability",
            f"{result['road_closure_probability'] * 100:.1f}%"
        )

        c3.metric(
            "Predicted Duration",
            f"{result['predicted_duration_minutes']:.0f} min"
        )

        c4.metric(
            "Priority",
            rec["priority"]
        )

        tii = result["traffic_impact_index"]

        if tii > 80:
            st.error("🚨 Critical Traffic Impact")
        elif tii > 60:
            st.warning("⚠️ High Traffic Impact")
        elif tii > 40:
            st.info("🔵 Medium Traffic Impact")
        else:
            st.success("🟢 Low Traffic Impact")

        # =====================================================
        # MAP
        # =====================================================

        st.divider()
        st.header("🗺 Incident Location")

        m = folium.Map(
            location=[12.97, 77.59],
            zoom_start=12
        )

        folium.Marker(
            [12.97, 77.59],
            popup=f"{corridor_name} Incident"
        ).add_to(m)

        st_folium(
            m,
            width=900,
            height=400
        )

        # =====================================================
        # RESOURCE ALLOCATION
        # =====================================================

        st.divider()
        st.header("🚓 Resource Allocation")

        r = rec["resources"]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Traffic Police", r["traffic_police"])
        c2.metric("Barricades", r["barricades"])
        c3.metric("Tow Trucks", r["tow_trucks"])
        c4.metric("Ambulances", r["ambulances"])

        st.metric(
            "Risk Score",
            round(rec["risk_score"], 2)
        )

        st.progress(
            min(rec["risk_score"] / 300, 1.0)
        )

        # =====================================================
        # RISK RANKING
        # =====================================================

        st.divider()
        st.header("📈 Corridor Risk Ranking")

        risk_df = pd.DataFrame({
            "Corridor": [
                "Outer Ring Road",
                "Mysore Road",
                "Bellary Road",
                "Bannerghatta Road"
            ],
            "Risk": [
                88,
                76,
                58,
                42
            ]
        })

        st.bar_chart(
            risk_df.set_index("Corridor")
        )

        # =====================================================
        # DIVERSION PLAN
        # =====================================================

        st.divider()
        st.header("🚧 Diversion Plan")

        diversion = rec["diversion"]

        if diversion["activate"]:

            st.warning(
                "Diversion Recommended"
            )

            for route in diversion["routes"]:
                st.success(route)

        else:

            st.info(
                "No Diversion Required"
            )

        # =====================================================
        # DOWNLOAD REPORT
        # =====================================================

        report = f"""
GRIDLOCK AI INCIDENT REPORT

Corridor: {corridor_name}
Junction: {junction_name}
Zone: {zone_name}

Traffic Impact Index:
{result['traffic_impact_index']}

Predicted Duration:
{result['predicted_duration_minutes']}

Closure Probability:
{result['road_closure_probability']}

Priority:
{rec['priority']}

Risk Score:
{rec['risk_score']}
"""

        st.download_button(
            "📄 Download Incident Report",
            report,
            file_name="incident_report.txt"
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )
  
  