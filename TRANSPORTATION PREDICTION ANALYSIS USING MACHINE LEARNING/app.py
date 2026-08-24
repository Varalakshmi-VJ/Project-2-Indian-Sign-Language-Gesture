import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="Transportation Prediction System",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 Transportation & Accident Prediction System")

# ---------------------------------
# Navigation Tabs
# ---------------------------------
tabs = st.tabs(["🏠 Home", "📊 Dashboard", "🚨 Live Prediction"])

# ======================================================
# 🏠 HOME TAB – DATASET
# ======================================================
with tabs[0]:
    st.header("🏠 Home")
    st.subheader("📂 Dataset Overview")

    # Sample dataset (replace with real CSV)
    data = pd.DataFrame({
        "Traffic Volume": np.random.randint(500, 5000, 100),
        "Avg Speed": np.random.randint(20, 100, 100),
        "Weather": np.random.choice(["Clear", "Rainy", "Foggy"], 100),
        "Accidents": np.random.randint(0, 5, 100)
    })

    st.dataframe(data.head(20))
    st.success("Dataset loaded successfully")

# ======================================================
# 📊 DASHBOARD TAB
# ======================================================
with tabs[1]:
    st.header("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🚗 Avg Traffic", int(data["Traffic Volume"].mean()))
    col2.metric("⚡ Avg Speed", int(data["Avg Speed"].mean()))
    col3.metric("🚨 Total Accidents", data["Accidents"].sum())
    col4.metric("📈 Max Traffic", data["Traffic Volume"].max())

    st.markdown("### 📈 Traffic Trends")
    st.line_chart(data["Traffic Volume"])

    st.markdown("### 🚨 Accident Distribution")
    st.bar_chart(data["Accidents"].value_counts())

# ======================================================
# 🚨 LIVE PREDICTION TAB
# ======================================================
with tabs[2]:
    st.header("🚨 Live Prediction")

    st.sidebar.header("📥 Input Parameters")

    traffic_volume = st.sidebar.slider("Traffic Volume", 100, 5000, 1500)
    avg_speed = st.sidebar.slider("Average Speed", 10, 120, 50)
    weather = st.sidebar.selectbox("Weather", ["Clear", "Rainy", "Foggy", "Snowy"])
    road_condition = st.sidebar.selectbox("Road Condition", ["Good", "Moderate", "Poor"])
    area_type = st.sidebar.selectbox("Area Type", ["Urban", "Semi-Urban", "Rural"])

    st.markdown("### 🔮 Prediction Output")

    if st.button("Predict"):
        # Simulated demand prediction
        predicted_demand = int(traffic_volume * np.random.uniform(0.8, 1.2))

        # Risk score calculation
        risk_score = 0

        if weather != "Clear":
            risk_score += 2

        if road_condition == "Poor":
            risk_score += 3

        if avg_speed > 80:
            risk_score += 2

        if traffic_volume > 3000:
            risk_score += 2

        # Area type impact
        if area_type == "Urban":
            risk_score += 2
        elif area_type == "Semi-Urban":
            risk_score += 1
        elif area_type == "Rural":
            risk_score += 1

        # Final risk classification
        risk = "Low" if risk_score <= 2 else "Medium" if risk_score <= 5 else "High"

        # Output
        st.success(f"📈 Predicted Demand: **{predicted_demand} trips/hour**")
        st.warning(f"🚨 Accident Risk Level: **{risk}**")
        st.info(f"📍 Area Type Selected: **{area_type}**")
