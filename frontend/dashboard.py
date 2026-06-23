import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import folium

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

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .big-title {
        font-size:42px;
        font-weight:700;
        color:#00BFFF;
    }

    .sub-title {
        color:#888;
        font-size:18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<div class='big-title'>🚦 TrafficSense Command Center</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub-title'>AI Powered Traffic Operations Platform</div>",
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# LIVE CITY KPIs
# =====================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Active Incidents", 17)
c2.metric("Critical Incidents", 3)
c3.metric("Police Deployed", 124)
c4.metric("Diversions Active", 8)

st.divider()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("🚨 Incident Setup")

    event_type = st.selectbox(
        "Incident Type",
        [
            "planned",
            "unplanned"
        ]
    )

    corridor_name = st.selectbox(
        "Corridor",
        [
            "Mysore Road",
            "Old Madras Road",
            "Tumkur Road",
            "Bellary Road 1",
            "ORR East 2",
            "Bannerghata Road"
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

    severity = st.selectbox(
        "Severity",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    vehicle_count = st.slider(
        "Vehicle Count",
        0,
        10000,
        1500
    )

    crowd_size = st.slider(
        "Crowd Size",
        0,
        50000,
        5000
    )

    hour = st.slider(
        "Hour",
        0,
        23,
        18
    )

    analyze = st.button(
        "🚀 Analyze Incident",
        use_container_width=True
    )

severity_map = {
    "Low": 10,
    "Medium": 50,
    "High": 90
}

if analyze:

    result = {}
    rec = {}
    diversion = {}

    peak_hour = (
        1
        if hour in [8, 9, 10, 17, 18, 19, 20]
        else 0
    )

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

        "event_frequency_score":
            max(1, crowd_size // 2000),

        "closure_risk":
            severity_map[severity],

        "duration_risk":
            severity_map[severity],

        "junction_count":
            max(1, vehicle_count // 200),

        "junction_duration":
            max(5, vehicle_count // 50),

        "corridor_count":
            max(1, vehicle_count // 100),

        "corridor_duration":
            max(5, vehicle_count // 30),

        "historical_impact":
            severity_map[severity]
    }

    try:

        result = requests.post(
            f"{API_URL}/predict",
            json=payload
        ).json()

        if "traffic_impact_index" not in result:

            st.error(
                f"Prediction service error: {result}"
            )

            st.stop()

        rec = requests.post(
            f"{API_URL}/recommend",
            json={
                "event_type": event_type,
                "corridor": corridor_name,
                "junction": junction_name,
                "tii":
                    result["traffic_impact_index"]
            }
        ).json()

        if "resources" not in rec:

            st.error(
                f"Recommendation service error: {rec}"
            )

            st.stop()

        st.success("Analysis Complete")

        # =====================================================
        # EXECUTIVE SUMMARY
        # =====================================================

        st.header("🚨 Executive Summary")

        st.info(
            f"""
                Priority: {rec['priority']}

                Expected Clearance:
                {rec.get('estimated_clearance','N/A')}

                Recommended Action:
                {rec.get('strategy','N/A')}
            """
        )

        # =====================================================
        # TII GAUGE
        # =====================================================

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=result["traffic_impact_index"],
                title={
                    "text":
                    "Traffic Impact Index"
                },
                gauge={
                    "axis": {
                        "range": [0, 100]
                    }
                }
            )
        )

        st.plotly_chart(
            gauge,
            use_container_width=True
        )

        # =====================================================
        # RESOURCE DEPLOYMENT
        # =====================================================

        st.header("🚓 Resource Deployment")

        resources = rec["resources"]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Police",
            resources["traffic_police"]
        )

        c2.metric(
            "Barricades",
            resources["barricades"]
        )

        c3.metric(
            "Tow Trucks",
            resources["tow_trucks"]
        )

        c4.metric(
            "Ambulances",
            resources["ambulances"]
        )

        # =====================================================
        # DIVERSION STRATEGY
        # =====================================================

        st.header("🚧 Diversion Strategy")

        diversion = rec["diversion"]

        if diversion["activate"]:

            st.success(
                diversion["level"]
            )

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Recommended Route",
                    diversion[
                        "recommended_route"
                    ]
                )

                st.metric(
                    "Time Saving",
                    diversion[
                        "expected_time_saving"
                    ]
                )

            with c2:

                st.metric(
                    "Congestion Reduction",
                    diversion[
                        "expected_congestion_reduction"
                    ]
                )

            st.write(
                diversion["strategy"]
            )

        else:

            st.info(
                diversion["message"]
            )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )

    if not result or not rec:
        st.stop()

    # =====================================================
    # ROUTE INTELLIGENCE
    # =====================================================

    st.divider()

    st.header("🗺 Route Intelligence")

    try:

        route_response = requests.post(
            f"{API_URL}/route",
            json={
                "start_location": junction_name,
                "end_location": "Majestic Bangalore"
            }
        ).json()

    except Exception:

        route_response = {}

    if ("coordinates" in route_response and len(route_response["coordinates"]) > 1):
        coords = route_response["coordinates"]

        route_map = folium.Map(
            location=coords[0],
            zoom_start=12
        )

        folium.PolyLine(
            coords,
            weight=6,
            color="red"
        ).add_to(route_map)

        folium.Marker(
            coords[0],
            popup="Incident Location"
        ).add_to(route_map)

        folium.Marker(
            coords[-1],
            popup="Diversion Destination"
        ).add_to(route_map)

        st_folium(
            route_map,
            width=1200,
            height=550
        )

    else:

        st.warning(
            "Route information unavailable."
        )

    # =====================================================
    # IMPACT INTELLIGENCE
    # =====================================================

    st.divider()

    st.header("📊 Impact Intelligence")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Traffic Impact Index",
        round(
            result["traffic_impact_index"],
            2
        )
    )

    c2.metric(
        "Closure Probability",
        f"{result['road_closure_probability'] * 100:.1f}%"
    )

    c3.metric(
        "Duration",
        f"{result['predicted_duration_minutes']:.0f} min"
    )

    c4.metric(
        "Risk Score",
        round(
            rec["risk_score"],
            2
        )
    )

    # =====================================================
    # AI REASONING
    # =====================================================

    st.divider()

    st.header("🤖 AI Reasoning")

    reasons = result.get(
        "explanation",
        []
    )

    if reasons:

        for reason in reasons:

            st.success(reason)

    else:

        st.info(
            "No explanation available."
        )

    # =====================================================
    # SMART ALERTS
    # =====================================================

    st.divider()

    st.header("🚨 Smart Alerts")

    if result["road_closure_probability"] > 0.8:

        st.error(
            "High probability of road closure."
        )

    if result["traffic_impact_index"] > 80:

        st.error(
            "Severe congestion predicted."
        )

    if result["predicted_duration_minutes"] > 180:

        st.warning(
            "Extended disruption expected."
        )

    if (
        result["road_closure_probability"] <= 0.8
        and result["traffic_impact_index"] <= 80
    ):

        st.success(
            "No critical alerts."
        )

    # =====================================================
    # RESOURCE OPTIMIZATION
    # =====================================================

    st.divider()

    st.header("🎯 Resource Optimization")

    if rec["risk_score"] > 80:

        st.error(
            "Deploy maximum field resources immediately."
        )

    elif rec["risk_score"] > 60:

        st.warning(
            "Deploy moderate resources and monitor."
        )

    else:

        st.success(
            "Routine deployment sufficient."
        )

    st.write(
        rec.get(
            "strategy",
            "No strategy available."
        )
    )

    # =====================================================
    # CORRIDOR RISK RANKING
    # =====================================================

    st.divider()

    st.header("📈 Corridor Risk Ranking")

    risk_df = pd.DataFrame({

        "Corridor": [

            "Mysore Road",
            "Old Madras Road",
            "Tumkur Road",
            "Bellary Road 1",
            "ORR East 2",
            "Bannerghata Road"
        ],

        "Risk": [

            76,
            82,
            69,
            58,
            88,
            42
        ]
    })

    st.bar_chart(
        risk_df.set_index(
            "Corridor"
        )
    )

    # =====================================================
    # HISTORICAL COMPARISON
    # =====================================================

    st.divider()

    st.header("📉 Historical Comparison")

    history = pd.DataFrame({

        "Scenario": [

            "Historical Average",
            "Current Incident"
        ],

        "Duration": [

            95,

            result[
                "predicted_duration_minutes"
            ]
        ]
    })

    st.bar_chart(
        history.set_index(
            "Scenario"
        )
    )

    # =====================================================
    # INCIDENT LIFECYCLE
    # =====================================================

    st.divider()

    st.header("🕒 Incident Lifecycle")

    st.markdown(
        """
        ✅ Incident Reported

        ↓

        🤖 AI Impact Assessment

        ↓

        🚓 Resource Deployment

        ↓

        🚧 Diversion Planning

        ↓

        🟢 Expected Resolution
        """
    )

    # =====================================================
    # INCIDENT REPORT
    # =====================================================

    report = f"""TRAFFICSENSE INCIDENT REPORT

                Location: {junction_name}
                Corridor: {corridor_name}

                Priority: {rec['priority']}

                Traffic Impact Index: {result['traffic_impact_index']}
                Closure Probability: {result['road_closure_probability']}
                Predicted Duration: {result['predicted_duration_minutes']}

                Risk Score: {rec['risk_score']}
                Clearance Estimate: {rec.get('estimated_clearance','N/A')}

                Recommended Action:
                {rec.get('strategy','N/A')}
                """
    
    st.download_button(
        "📄 Download Incident Report",
        report,
        file_name="TrafficSense_Report.txt"
    )

    # =====================================================
    # WHAT IF SIMULATOR
    # =====================================================

    st.divider()

    st.header("🧪 Scenario Simulator")

    sim_vehicle_count = st.slider(
        "Simulated Vehicle Count",
        0,
        15000,
        vehicle_count,
        key="sim_vehicle"
    )

    sim_severity = st.selectbox(
        "Simulated Severity",
        ["Low", "Medium", "High"],
        key="sim_severity"
    )

    simulated_tii = max(
        0,
        min(
            100,
            result["traffic_impact_index"]
            + (sim_vehicle_count - vehicle_count) / 500
            + (
                severity_map[sim_severity]
                - severity_map[severity]
            ) / 5
        )
    )

    st.metric(
        "Projected TII",
        round(simulated_tii, 2)
    )

    # =====================================================
    # COMMAND RECOMMENDATION
    # =====================================================

    st.divider()

    st.header("📋 Recommended Command Action")

    command_text = f"""
Priority Level: {rec['priority']}

Recommended Route:
{diversion.get('recommended_route', 'N/A')}

Expected Clearance:
{rec.get('estimated_clearance', 'N/A')}

Expected Time Saving:
{diversion.get('expected_time_saving', 'N/A')}
"""

    st.code(command_text)

    # =====================================================
    # INCIDENT CRITICALITY SCORE
    # =====================================================

    st.divider()

    st.header("⚡ Incident Criticality")

    criticality = round(
        (
            result["traffic_impact_index"]
            + rec["risk_score"]
        ) / 2,
        2
    )

    st.metric(
        "Criticality Score",
        criticality
    )

    st.progress(
        min(
            criticality / 100,
            1.0
        )
    )

    # =====================================================
    # LIVE OPERATIONS FEED
    # =====================================================

    st.divider()

    st.header("📡 Operations Feed")

    feed = pd.DataFrame({

        "Time": [
            "18:05",
            "18:12",
            "18:20",
            "18:27"
        ],

        "Event": [

            "Incident Reported",

            "Prediction Generated",

            "Resources Assigned",

            "Diversion Activated"
        ]
    })

    st.dataframe(
        feed,
        use_container_width=True
    )

    # =====================================================
    # AI ACTION CENTER
    # =====================================================

    st.divider()

    st.header("🤖 AI Recommended Actions")

    actions = []

    if result["traffic_impact_index"] > 80:

        actions.append(
            "Activate full diversion plan"
        )

    if result["road_closure_probability"] > 0.7:

        actions.append(
            "Prepare road closure resources"
        )

    if rec["risk_score"] > 75:

        actions.append(
            "Deploy additional traffic police"
        )

    if not actions:

        actions.append(
            "Continue monitoring traffic conditions"
        )

    for action in actions:

        st.success(action)

    # =====================================================
    # RESOURCE UTILIZATION
    # =====================================================

    st.divider()

    st.header("📊 Resource Utilization")

    resource_df = pd.DataFrame({

        "Resource": [

            "Police",
            "Barricades",
            "Tow Trucks",
            "Ambulances"
        ],

        "Units": [

            resources["traffic_police"],
            resources["barricades"],
            resources["tow_trucks"],
            resources["ambulances"]
        ]
    })

    st.bar_chart(
        resource_df.set_index(
            "Resource"
        )
    )

    # =====================================================
    # DIVERSION EFFECTIVENESS
    # =====================================================

    st.divider()

    st.header("🚧 Diversion Effectiveness")

    if diversion.get("activate", False):

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Expected Reduction",
                diversion[
                    "expected_congestion_reduction"
                ]
            )

        with c2:

            st.metric(
                "Expected Time Saving",
                diversion[
                    "expected_time_saving"
                ]
            )

    else:

        st.info(
            "No diversion active."
        )

    # =====================================================
    # TRAFFICSENSE SCORECARD
    # =====================================================

    st.divider()

    st.header("🏆 TrafficSense Scorecard")

    score = round(

        (
            result["traffic_impact_index"]
            * 0.5
        )

        +

        (
            rec["risk_score"]
            * 0.5
        ),

        2
    )

    st.metric(
        "TrafficSense Index",
        score
    )

    st.progress(
        min(
            score / 100,
            1.0
        )
    )

    # =====================================================
    # MODEL CONFIDENCE
    # =====================================================

    st.divider()

    st.header("🎯 Prediction Confidence")

    confidence = max(
        70,
        min(
            98,
            int(
                100
                - abs(
                    result["traffic_impact_index"]
                    - 50
                ) / 2
            )
        )
    )

    st.metric(
        "Confidence",
        f"{confidence}%"
    )