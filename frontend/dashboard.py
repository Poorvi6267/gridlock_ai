import streamlit as st
import requests

st.set_page_config(
    page_title="Gridlock AI",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 Gridlock AI")
st.subheader("Traffic Impact Prediction & Resource Allocation")

event_type = st.selectbox(
    "Event Type",
    ["planned", "unplanned"]
)

corridor = st.text_input(
    "Corridor",
    "Mysore Road"
)

junction = st.text_input(
    "Junction",
    "Nagavara-ORR Junction"
)

tii = st.slider(
    "Traffic Impact Index",
    0,
    100,
    88
)

if st.button("Predict"):

    payload = {
        "event_type": event_type,
        "corridor": corridor,
        "junction": junction,
        "tii": tii
    }

    response = requests.post(
        "http://127.0.0.1:8000/recommend",
        json=payload
    )

    
    result = response.json()
    
    st.success("Prediction Complete")
    
    priority = result["priority"]
    
    if priority == "Critical":
        st.error("🚨 CRITICAL INCIDENT")

    elif priority == "High":
        st.warning("⚠️ HIGH IMPACT")

    else:
        st.success("✅ LOW IMPACT")
        
    risk = result["risk_score"]

    st.metric(
        "Risk Score",
        round(risk,2)
    )

    st.progress(min(risk/200,1.0))

    st.subheader("🚓 Resources")

    r = result["resources"]

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "🚓 Police",
        r["traffic_police"]
    )

    c2.metric(
        "🚑 Ambulances",
        r["ambulances"]
    )

    c3.metric(
        "🚚 Tow Trucks",
        r["tow_trucks"]
    )

    c4.metric(
        "🚧 Barricades",
        r["barricades"]
    )

    st.subheader("🚧 Diversion Plan")

    d = result["diversion"]

    if d["activate"]:
        st.success("Diversion Recommended")
    else:
        st.info("No Diversion Required")

    st.subheader("Suggested Routes")

    for route in d["routes"]:
        st.info(route)
    
