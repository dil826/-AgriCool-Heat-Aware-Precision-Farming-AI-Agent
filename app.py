import json
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.ai_agent import AgriAdvisorAgent
from src.fortyguard_client import FortyGuardClient
from src.heat_calculator import (
    calculate_heat_index,
    estimate_irrigation_need,
    heat_risk_level,
)
from src.weather_client import WeatherClient


load_dotenv()

st.set_page_config(page_title="AgriCool", page_icon="🌾", layout="wide")
st.title("🌾 AgriCool: Heat-Aware Precision Farming AI Agent")
st.caption("Built for FortyGuard Global AI Hackathon '26")

thresholds_path = Path("data/crop_thresholds.json")
with thresholds_path.open("r", encoding="utf-8") as f:
    crop_thresholds = json.load(f)

with st.sidebar:
    st.header("Field Inputs")
    lat = st.number_input("Latitude", value=12.9716, format="%.4f")
    lon = st.number_input("Longitude", value=77.5946, format="%.4f")
    crop = st.selectbox("Crop Type", options=list(crop_thresholds.keys()))
    refresh = st.button("Refresh Climate Data")

if "climate_data" not in st.session_state or refresh:
    fg_client = FortyGuardClient()
    wx_client = WeatherClient()

    temp_data = fg_client.fetch_temperature(lat, lon)
    env_data = wx_client.fetch_conditions(lat, lon)

    heat_index_c = calculate_heat_index(temp_data["temperature_c"], env_data["humidity"])
    irrigation = estimate_irrigation_need(
        temperature_c=temp_data["temperature_c"],
        heat_index_c=heat_index_c,
        crop_profile=crop_thresholds[crop],
        precipitation_mm=env_data["precipitation"],
    )

    st.session_state.climate_data = {
        "temperature_c": temp_data["temperature_c"],
        "source": temp_data["source"],
        "heat_index_c": heat_index_c,
        "risk_level": heat_risk_level(heat_index_c),
        "humidity": env_data["humidity"],
        "wind_speed": env_data["wind_speed"],
        "precipitation": env_data["precipitation"],
        "irrigation": irrigation,
    }

climate = st.session_state.climate_data

col1, col2, col3 = st.columns(3)
col1.metric("Current Field Temperature", f"{climate['temperature_c']:.1f} °C", climate["source"])
col2.metric("Heat Index Risk", climate["risk_level"], f"{climate['heat_index_c']:.1f} °C")
col3.metric(
    "Estimated Irrigation Need",
    f"{climate['irrigation']['irrigation_mm_day']:.1f} mm/day",
    climate["irrigation"]["water_stress_severity"],
)

st.subheader("Microclimate Summary")
summary_df = pd.DataFrame(
    {
        "Metric": ["Humidity (%)", "Wind Speed (m/s)", "Precipitation (mm)", "Water Loss (L/ha/day)"],
        "Value": [
            climate["humidity"],
            climate["wind_speed"],
            climate["precipitation"],
            climate["irrigation"]["water_loss_l_ha_day"],
        ],
    }
)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.subheader("Ask AgriCool Advisor")
user_question = st.text_input(
    "Ask a farming question",
    placeholder="How should I schedule irrigation for tomorrow?",
)

if user_question:
    agent = AgriAdvisorAgent()
    with st.spinner("Generating heat-aware recommendation..."):
        reply = agent.get_recommendation(
            crop_type=crop,
            temperature_c=climate["temperature_c"],
            heat_index_c=climate["heat_index_c"],
            farmer_question=user_question,
        )
    st.markdown("### AI Recommendation")
    st.write(reply)
