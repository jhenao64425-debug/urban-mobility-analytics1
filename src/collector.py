"""Orquestador principal de recolección de datos de tráfico y clima."""

import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from src.database import RouteDatabase
from src.locations import ROUTES, get_all_unique_locations
from src.tomtom_client import TomTomClient
from src.weather_client import WeatherClient

logger = logging.getLogger(__name__)


class DataCollector:
    """Recolector de datos de tráfico y clima para rutas en Malta."""

    def __init__(self, tomtom_key: str, weather_key: str, csv_path: Path, db_path: Path):
        self.tomtom = TomTomClient(tomtom_key)
        self.weather = WeatherClient(weather_key)
        self.db = RouteDatabase(csv_path, db_path)
        self.running = True

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Maneja Ctrl+C para detener gracefully."""
        logger.info("Stopping collector...")
        self.running = False
        self.tomtom.close()
        self.weather.close()
        sys.exit(0)

    def collect_cycle(self) -> int:
        """
        Ejecuta un ciclo completo de recolección.

        Retorna el número de registros guardados exitosamente.
        """
        logger.info("Starting collection cycle")

        timestamp_utc = datetime.now(timezone.utc).isoformat()
        records: List[dict] = []

        unique_locations = get_all_unique_locations()
        weather_data = {}

        for location_name, location in unique_locations.items():
            try:
                weather_data[location_name] = self.weather.get_current_weather(
                    location.latitude,
                    location.longitude,
                )
            except Exception as e:
                logger.warning(
                    f"Weather fetch failed for {location_name}: {e}. "
                    f"Will continue with other routes."
                )

        for origin_name, destination_name in ROUTES:
            try:
                origin = get_all_unique_locations()[origin_name]
                destination = get_all_unique_locations()[destination_name]

                route_data = self.tomtom.calculate_route(
                    origin.latitude,
                    origin.longitude,
                    destination.latitude,
                    destination.longitude,
                )

                record = {
                    "timestamp": timestamp_utc,
                    "origin": origin_name,
                    "destination": destination_name,
                    **route_data,
                }

                origin_weather = weather_data.get(origin_name, {})
                destination_weather = weather_data.get(destination_name, {})

                record["origin_temperature"] = origin_weather.get("temperature")
                record["origin_feels_like"] = origin_weather.get("feels_like")
                record["origin_humidity"] = origin_weather.get("humidity")
                record["origin_weather"] = origin_weather.get("weather")

                record["destination_temperature"] = destination_weather.get("temperature")
                record["destination_feels_like"] = destination_weather.get("feels_like")
                record["destination_humidity"] = destination_weather.get("humidity")
                record["destination_weather"] = destination_weather.get("weather")

                records.append(record)

                logger.info(
                    f"{origin_name}→{destination_name}: {route_data['travel_time_min']:.1f}min "
                    f"(+{route_data['traffic_delay_min']:.1f}min delay)"
                )

            except Exception as e:
                logger.error(
                    f"Failed to collect {origin_name} → {destination_name}: {e}"
                )
                continue

        if not records:
            logger.error("No records were collected successfully")
            return 0

        try:
            self.db.save_records_to_csv(records)
            self.db.save_records_to_sqlite(records)
            logger.info(f"Successfully saved {len(records)} records")
            return len(records)
        except Exception as e:
            logger.error(f"Failed to save records: {e}")
            return 0

    def run_once(self) -> None:
        """Ejecuta un solo ciclo de recolección."""
        self.collect_cycle()

    def run_continuous(self, interval_seconds: int) -> None:
        """
        Ejecuta recolecciones continuas cada N segundos.

        Detiene correctamente con Ctrl+C.
        """
        logger.info(f"Starting continuous collection (interval: {interval_seconds}s)")

        while self.running:
            self.collect_cycle()

            if not self.running:
                break

            logger.info(f"Next collection in {interval_seconds} seconds...")
            for _ in range(interval_seconds):
                if not self.running:
                    break
                time.sleep(1)

        logger.info("Collector stopped")
