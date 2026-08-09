"""
Recolector principal de datos de tráfico y clima para rutas en Malta.

Uso:
    python src/route_extraction.py                      # Una ejecución
    python src/route_extraction.py --interval 120       # Continuo cada 120 segundos
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.collector import DataCollector

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
CSV_PATH = ROOT_DIR / "data" / "raw" / "route_weather_data.csv"
DB_PATH = ROOT_DIR / "data" / "mobility.db"
LOG_DIR = ROOT_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "collector.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

load_dotenv(ENV_PATH)

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def validate_keys() -> None:
    """Valida que las claves API estén configuradas."""
    if not TOMTOM_API_KEY:
        raise RuntimeError("Missing TOMTOM_API_KEY in .env file")
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("Missing OPENWEATHER_API_KEY in .env file")

    logger.info("API keys validated")


def main() -> None:
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Urban Mobility Analytics - Data Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/route_extraction.py                    # Run once
  python src/route_extraction.py --interval 120     # Run continuously every 120 seconds
        """,
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Interval in seconds for continuous collection. If not provided, runs once.",
    )

    args = parser.parse_args()

    try:
        validate_keys()
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    collector = DataCollector(
        TOMTOM_API_KEY,
        OPENWEATHER_API_KEY,
        CSV_PATH,
        DB_PATH,
    )

    try:
        if args.interval:
            if args.interval < 30:
                logger.warning("Interval is very short. Minimum recommended is 30 seconds.")
            logger.info(f"Starting continuous collection every {args.interval} seconds")
            collector.run_continuous(args.interval)
        else:
            logger.info("Starting single collection cycle")
            collector.run_once()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()