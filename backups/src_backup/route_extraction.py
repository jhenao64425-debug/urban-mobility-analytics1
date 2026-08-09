from datetime import datetime, timezone
from pathlib import Path
import os

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURACIÓN DEL PROYECTO
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
CSV_PATH = ROOT_DIR / "data" / "raw" / "route_weather_data.csv"

load_dotenv(ENV_PATH)

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ============================================================
# UBICACIONES Y RUTAS
# Coordenadas aproximadas de diferentes localidades de Malta.
# ============================================================

LOCATIONS = {
    "Msida": (35.8970, 14.4890),
    "Gzira": (35.9059, 14.4950),
    "Sliema": (35.9122, 14.5040),
    "Valletta": (35.8989, 14.5146),
    "St Julian's": (35.9181, 14.4898),
    "Birkirkara": (35.8972, 14.4611),
    "Marsaskala": (35.8620, 14.5670),
}


ROUTES = [
    ("Msida", "Gzira"),
    ("Msida", "Sliema"),
    ("Msida", "Valletta"),
    ("Msida", "St Julian's"),
    ("Msida", "Birkirkara"),
    ("Msida", "Marsaskala"),
]


# El clima se consulta desde Msida.
WEATHER_LOCATION = LOCATIONS["Msida"]


# ============================================================
# VALIDACIÓN DE CLAVES
# ============================================================

def require_key(value: str | None, name: str) -> str:
    """Comprueba que la clave API existe."""

    if not value:
        raise RuntimeError(
            f"Missing {name} in the .env file."
        )

    return value


# ============================================================
# DATOS DE RUTA CON TOMTOM
# ============================================================

def get_route_data(
    origin_coordinates: tuple[float, float],
    destination_coordinates: tuple[float, float],
) -> dict:
    """Obtiene distancia, duración y tráfico de una ruta."""

    tomtom_key = require_key(
        TOMTOM_API_KEY,
        "TOMTOM_API_KEY",
    )

    origin = (
        f"{origin_coordinates[0]},"
        f"{origin_coordinates[1]}"
    )

    destination = (
        f"{destination_coordinates[0]},"
        f"{destination_coordinates[1]}"
    )

    url = (
        "https://api.tomtom.com/routing/1/"
        f"calculateRoute/{origin}:{destination}/json"
    )

    params = {
        "key": tomtom_key,
        "traffic": "true",
        "travelMode": "car",
        "routeType": "fastest",
        "computeTravelTimeFor": "all",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()
    routes = payload.get("routes", [])

    if not routes:
        raise RuntimeError(
            "TomTom did not return any route."
        )

    summary = routes[0]["summary"]

    distance_km = (
        summary["lengthInMeters"] / 1000
    )

    travel_time_min = (
        summary["travelTimeInSeconds"] / 60
    )

    traffic_delay_min = (
        summary.get("trafficDelayInSeconds", 0) / 60
    )

    no_traffic_seconds = summary.get(
        "noTrafficTravelTimeInSeconds",
        max(
            0,
            summary["travelTimeInSeconds"]
            - summary.get(
                "trafficDelayInSeconds",
                0,
            ),
        ),
    )

    no_traffic_time_min = (
        no_traffic_seconds / 60
    )

    average_speed_kmh = (
        distance_km / (travel_time_min / 60)
        if travel_time_min > 0
        else 0
    )

    return {
        "distance_km": round(distance_km, 2),
        "travel_time_min": round(
            travel_time_min,
            2,
        ),
        "no_traffic_time_min": round(
            no_traffic_time_min,
            2,
        ),
        "traffic_delay_min": round(
            traffic_delay_min,
            2,
        ),
        "traffic_length_km": round(
            summary.get(
                "trafficLengthInMeters",
                0,
            ) / 1000,
            2,
        ),
        "average_speed_kmh": round(
            average_speed_kmh,
            2,
        ),
        "departure_time": summary.get(
            "departureTime"
        ),
        "arrival_time": summary.get(
            "arrivalTime"
        ),
    }


# ============================================================
# DATOS DEL CLIMA CON OPENWEATHER
# ============================================================

def get_weather_data(
    coordinates: tuple[float, float],
) -> dict:
    """Obtiene el clima actual para unas coordenadas."""

    weather_key = require_key(
        OPENWEATHER_API_KEY,
        "OPENWEATHER_API_KEY",
    )

    url = (
        "https://api.openweathermap.org/"
        "data/2.5/weather"
    )

    params = {
        "lat": coordinates[0],
        "lon": coordinates[1],
        "appid": weather_key,
        "units": "metric",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    main_data = payload.get("main", {})
    weather_items = payload.get("weather", [])

    weather_description = (
        weather_items[0].get(
            "description",
            "Unknown",
        )
        if weather_items
        else "Unknown"
    )

    return {
        "temperature": main_data.get("temp"),
        "feels_like": main_data.get(
            "feels_like"
        ),
        "humidity": main_data.get("humidity"),
        "weather": weather_description,
    }


# ============================================================
# GUARDAR REGISTROS EN CSV
# ============================================================

def save_records(records: list[dict]) -> None:
    """Añade todas las rutas recopiladas al CSV."""

    if not records:
        return

    CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = pd.DataFrame(records)

    file_exists = (
        CSV_PATH.exists()
        and CSV_PATH.stat().st_size > 0
    )

    dataframe.to_csv(
        CSV_PATH,
        mode="a",
        header=not file_exists,
        index=False,
    )


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main() -> None:
    """Recoge clima y tráfico para todas las rutas."""

    print("\nCollecting route information...")

    weather = get_weather_data(
        WEATHER_LOCATION
    )

    cycle_timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    records: list[dict] = []

    for origin_name, destination_name in ROUTES:
        try:
            route_data = get_route_data(
                LOCATIONS[origin_name],
                LOCATIONS[destination_name],
            )

            record = {
                "timestamp": cycle_timestamp,
                "origin": origin_name,
                "destination": destination_name,
                **route_data,
                **weather,
            }

            records.append(record)

            print(
                f"\n{origin_name} → "
                f"{destination_name}"
            )
            print(
                "Travel time: "
                f"{record['travel_time_min']} min"
            )
            print(
                "Without traffic: "
                f"{record['no_traffic_time_min']} min"
            )
            print(
                "Traffic delay: "
                f"{record['traffic_delay_min']} min"
            )
            print(
                "Distance: "
                f"{record['distance_km']} km"
            )
            print(
                "Average speed: "
                f"{record['average_speed_kmh']} km/h"
            )
            print(
                "Temperature: "
                f"{record['temperature']} °C"
            )
            print(
                "Humidity: "
                f"{record['humidity']}%"
            )
            print(
                f"Weather: {record['weather']}"
            )

        except requests.RequestException as error:
            print(
                f"\nError collecting "
                f"{origin_name} → "
                f"{destination_name}: {error}"
            )

        except (KeyError, RuntimeError) as error:
            print(
                f"\nCould not process "
                f"{origin_name} → "
                f"{destination_name}: {error}"
            )

    if not records:
        raise RuntimeError(
            "No route information could be collected."
        )

    save_records(records)

    print(
        "\nData saved successfully to "
        f"{CSV_PATH}"
    )
    print(
        f"Routes saved: {len(records)}"
    )


if __name__ == "__main__":
    main()