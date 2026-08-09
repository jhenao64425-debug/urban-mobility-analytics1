# Urban Mobility Analytics 🚗

Real-time traffic and weather monitoring for routes in Malta. Built with Python, TomTom API, and OpenWeather API.

## Project Status

**FASE 1 ✅** - Refactored collector with modular architecture, logging, and continuous execution support.  
**FASE 2 ✅** - SQLite integration, data migration, and historical analytics.  
**FASE 3** - Professional Streamlit dashboard (pending).  
**FASE 4** - Predictive models and deployment (pending).

## Features

- ✅ Collect real-time traffic data from TomTom API
- ✅ Fetch weather data from OpenWeather API
- ✅ Track 6 predefined routes in Malta
- ✅ Store data in CSV and SQLite
- ✅ Retry logic with exponential backoff
- ✅ Weather caching to avoid duplicate requests
- ✅ Structured logging to file and console
- ✅ Continuous collection with configurable intervals
- ✅ Graceful shutdown with Ctrl+C

### Routes Monitored

- Msida → Gzira
- Msida → Sliema
- Msida → Valletta
- Msida → St Julian's
- Msida → Birkirkara
- Msida → Marsaskala

## Architecture

```
src/
├── __init__.py                # Package initialization
├── locations.py               # Centralized locations and routes config
├── config.py                  # Environment variable management
├── tomtom_client.py          # TomTom API client with retries
├── weather_client.py         # OpenWeather API client with caching
├── database.py               # CSV and SQLite storage layer
├── collector.py              # Main orchestration logic
└── route_extraction.py       # CLI entry point

data/
├── raw/
│   └── route_weather_data.csv   # Historical CSV data
└── mobility.db                  # SQLite database

streamlit_app/
└── app.py                       # Dashboard (to be refactored)

logs/
└── collector.log               # Collector logs
```

## Installation

### Prerequisites

- Python 3.13+
- Virtual environment (recommended)

### Setup

```bash
cd urban-mobility-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Configure API Keys

Edit `.env` and add your API keys:

```
TOMTOM_API_KEY=your_tomtom_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Get your keys from:
- [TomTom API](https://developer.tomtom.com/)
- [OpenWeather API](https://openweathermap.org/api)

## Usage

### Single Collection Cycle

```bash
python -m src.route_extraction
```

### Continuous Collection

Collect data every 120 seconds:

```bash
python -m src.route_extraction --interval 120
```

Stop with `Ctrl+C` for graceful shutdown.

### View Logs

```bash
tail -f logs/collector.log
```

## Database

### CSV Storage

- **Location**: `data/raw/route_weather_data.csv`
- **Format**: Appended records, no overwrite
- **Updated**: Each collection cycle

### SQLite Storage

- **Location**: `data/mobility.db`
- **Table**: `route_measurements`
- **Indexes**: timestamp, origin, destination
- **Updated**: Each collection cycle
- **Duplicate Prevention**: UNIQUE constraint on (timestamp, origin, destination)

### Collected Metrics

Per route measurement:

- **Timestamp**: UTC ISO 8601
- **Route**: origin, destination
- **Distance**: distance_km
- **Time**: travel_time_min, no_traffic_time_min, traffic_delay_min
- **Traffic**: traffic_length_km, average_speed_kmh
- **ETimes**: departure_time, arrival_time (ISO format)
- **Origin Weather**: temperature, feels_like, humidity, weather description
- **Destination Weather**: temperature, feels_like, humidity, weather description
- **Route Geometry**: polyline (if available from API)

## Monitoring

### Check Database Status

```bash
sqlite3 data/mobility.db "SELECT COUNT(*) FROM route_measurements;"
sqlite3 data/mobility.db "SELECT DISTINCT origin, destination FROM route_measurements;"
```

### Recent Measurements

```bash
sqlite3 -header -column data/mobility.db \
  "SELECT timestamp, origin, destination, travel_time_min, traffic_delay_min FROM route_measurements ORDER BY timestamp DESC LIMIT 10;"
```

## Data Migration

Import historical CSV data to SQLite:

```bash
# Dry run preview
python -m src.migration --dry-run

# Actual migration
python -m src.migration --skip-confirmation
```

## Historical Analysis

Analyze trends and patterns:

```bash
# Summary report
python -m src.analytics summary

# Route trend analysis
python -m src.analytics trend Msida Gzira

# Weather impact analysis
python -m src.analytics weather Msida Sliema

# Consistency score
python -m src.analytics consistency Msida Valletta

# Compare all routes
python -m src.analytics compare
```

## Testing

```bash
# Test locations module
python tests/test_locations.py

# Test database module
python tests/test_database.py

# Test analytics module
python tests/test_analytics.py

# Run all tests
for test in tests/test_*.py; do python $test; done
```

## Security

- ⚠️ **Never commit `.env` file**
- ⚠️ **API keys stored only in `.env`** (added to .gitignore)
- ⚠️ **Logs do not contain sensitive data**
- Validate all external API responses before storing

## Troubleshooting

### "Missing TOMTOM_API_KEY"

Ensure `.env` file exists with valid key:

```bash
cat .env
# Should show: TOMTOM_API_KEY=...
```

### No Data in Database

Check logs:

```bash
tail logs/collector.log
```

Common issues:
- API rate limiting (wait 60 seconds)
- Invalid coordinates
- Network connectivity

### Duplicate Records

SQLite uses UNIQUE constraint to prevent exact duplicates. CSV may have duplicates if timestamp/origin/destination are identical.

## Next Steps

- **FASE 2**: SQLite optimization, data migration, historical analysis
- **FASE 3**: Professional dashboard with route selection, filtering, visualizations
- **FASE 4**: Predictive models for travel time, alerting system

## License

Internal use only. Do not redistribute without permission.

## Support

For issues or questions, check:
1. `logs/collector.log` for detailed error messages
2. API documentation links above
3. Project roadmap in FASE descriptions

---

**Last Updated**: 2026-07-19  
**Current Status**: FASE 1 Complete ✅
