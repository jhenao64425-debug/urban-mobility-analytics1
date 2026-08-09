from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "data" / "raw" / "route_weather_data.csv"

MSIDA = {"lat": 35.8970, "lon": 14.4890}
MARSASKALA = {"lat": 35.8620, "lon": 14.5670}


st.set_page_config(
    page_title="Urban Mobility Analytics",
    page_icon="🚗",
    layout="wide",
)

# Actualiza la página automáticamente cada 20 segundos.
st_autorefresh(interval=120_000, key="route_data_refresh")

st.title("🚗 Urban Mobility Analytics")
st.caption("Live route monitoring: Msida → Marsaskala")

if not CSV_PATH.exists():
    st.error(f"No se encontró el archivo de datos: {CSV_PATH}")
    st.stop()

df = pd.read_csv(CSV_PATH)

if df.empty:
    st.warning("El archivo existe, pero todavía no contiene mediciones.")
    st.stop()

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
    utc=True,
)

df = df.dropna(subset=["timestamp"])
df = df.sort_values("timestamp")

# Convertir las horas a la zona horaria de Malta.
df["malta_time"] = df["timestamp"].dt.tz_convert("Europe/Malta")

latest = df.iloc[-1]

travel_time = float(latest.get("travel_time_min", 0))
normal_time = float(latest.get("no_traffic_time_min", 0))
traffic_delay = float(latest.get("traffic_delay_min", 0))
distance = float(latest.get("distance_km", 0))
average_speed = float(latest.get("average_speed_kmh", 0))
temperature = float(latest.get("temperature", 0))
humidity = float(latest.get("humidity", 0))

congestion_percentage = (
    traffic_delay / travel_time * 100
    if travel_time > 0
    else 0
)

if traffic_delay <= 1:
    traffic_status = "🟢 Light traffic"
elif traffic_delay <= 4:
    traffic_status = "🟠 Moderate traffic"
else:
    traffic_status = "🔴 Heavy traffic"

st.subheader("Msida → Marsaskala")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Travel time",
    f"{travel_time:.1f} min",
    delta=f"{traffic_delay:.1f} min traffic delay",
    delta_color="inverse",
)

col2.metric(
    "Without traffic",
    f"{normal_time:.1f} min",
)

col3.metric(
    "Distance",
    f"{distance:.2f} km",
)

col4.metric(
    "Average speed",
    f"{average_speed:.1f} km/h",
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Traffic delay",
    f"{traffic_delay:.1f} min",
)

col6.metric(
    "Congestion",
    f"{congestion_percentage:.1f}%",
)

col7.metric(
    "Temperature",
    f"{temperature:.1f} °C",
)

col8.metric(
    "Humidity",
    f"{humidity:.0f}%",
)

weather = str(latest.get("weather", "Unknown")).title()
last_update = latest["malta_time"].strftime("%d/%m/%Y %H:%M:%S")

st.info(
    f"{traffic_status} · Weather: {weather} · "
    f"Last update: {last_update}"
)

arrival_value = latest.get("arrival_time")

if pd.notna(arrival_value):
    arrival = pd.to_datetime(
        arrival_value,
        errors="coerce",
        utc=True,
    )

    if pd.notna(arrival):
        arrival_malta = arrival.tz_convert("Europe/Malta")
        st.success(
            f"Estimated arrival: {arrival_malta.strftime('%H:%M:%S')}"
        )

st.subheader("Route location")

map_data = pd.DataFrame(
    [
        {
            "location": "Msida",
            "lat": MSIDA["lat"],
            "lon": MSIDA["lon"],
        },
        {
            "location": "Marsaskala",
            "lat": MARSASKALA["lat"],
            "lon": MARSASKALA["lon"],
        },
    ]
)

st.map(map_data, latitude="lat", longitude="lon")

chart_df = df.set_index("malta_time")

st.subheader("Travel-time evolution")

travel_columns = [
    column
    for column in [
        "travel_time_min",
        "no_traffic_time_min",
    ]
    if column in chart_df.columns
]

if travel_columns:
    st.line_chart(chart_df[travel_columns])

st.subheader("Traffic-delay evolution")

if "traffic_delay_min" in chart_df.columns:
    st.line_chart(chart_df[["traffic_delay_min"]])

weather_col1, weather_col2 = st.columns(2)

with weather_col1:
    st.subheader("Temperature evolution")

    if "temperature" in chart_df.columns:
        st.line_chart(chart_df[["temperature"]])

with weather_col2:
    st.subheader("Humidity evolution")

    if "humidity" in chart_df.columns:
        st.line_chart(chart_df[["humidity"]])

st.subheader("Latest collected records")

visible_columns = [
    column
    for column in [
        "malta_time",
        "origin",
        "destination",
        "travel_time_min",
        "no_traffic_time_min",
        "traffic_delay_min",
        "distance_km",
        "average_speed_kmh",
        "temperature",
        "humidity",
        "weather",
    ]
    if column in df.columns
]

st.dataframe(
    df[visible_columns].tail(50).sort_values(
        "malta_time",
        ascending=False,
    ),
    use_container_width=True,
    hide_index=True,
)