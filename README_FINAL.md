# Urban Mobility Analytics 🚗

Professional real-time traffic and weather monitoring dashboard for routes in Malta, built with Python, TomTom API, OpenWeather API, Streamlit, and scikit-learn.

**Status**: Production-Ready | **Version**: 1.0.0 | **Python**: 3.13+

## Overview

Urban Mobility Analytics is a comprehensive system for collecting, analyzing, and predicting travel times across multiple routes in Malta. It combines real-time API data with historical analysis and machine learning predictions to provide actionable insights for route planning and traffic optimization.

### Key Features

- ✅ **Real-time Data Collection** - TomTom routing & OpenWeather data every N seconds
- ✅ **Professional Dashboard** - Interactive Streamlit UI with filters & visualizations
- ✅ **Historical Analysis** - 305+ records with hourly patterns and weather impact
- ✅ **Predictive Models** - Travel time predictions using Random Forest (sklearn)
- ✅ **Smart Alerts** - Automatic detection of high delays and data staleness
- ✅ **Multi-Route Support** - 6 predefined routes, easily extensible
- ✅ **Dual Storage** - CSV backup + SQLite primary database
- ✅ **Export Features** - Download data as CSV or JSON
- ✅ **Robust Error Handling** - Retries with exponential backoff

## Project Structure

```
urban-mobility-analytics/
├── src/
│   ├── __init__.py
│   ├── config.py                      # Environment & API key management
│   ├── locations.py                   # Route & location definitions
│   ├── tomtom_client.py               # TomTom API client with retries
│   ├── weather_client.py              # OpenWeather client with caching
│   ├── database.py                    # SQLite & CSV storage layer
│   ├── collector.py                   # Main orchestration logic
│   ├── route_extraction.py            # CLI entry point
│   ├── migration.py                   # CSV → SQLite data import
│   ├── analytics.py                   # Historical analysis & reporting
│   ├── predictor.py                   # Prediction orchestrator
│   └── models/
│       ├── __init__.py
│       ├── travel_time_model.py       # Random Forest predictor
│       └── trained/                   # Serialized model files
│
├── streamlit_app/
│   ├── __init__.py
│   ├── app.py                         # Main dashboard
│   └── components.py                  # Reusable UI components
│
├── tests/
│   ├── __init__.py
│   ├── test_locations.py
│   ├── test_database.py
│   └── test_analytics.py
│
├── data/
│   ├── raw/
│   │   └── route_weather_data.csv    # Historical CSV backup
│   ├── mobility.db                    # SQLite database
│   └── processed/
│
├── logs/
│   └── collector.log                  # Application logs
│
├── backups/                           # Initial backup files
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .gitignore                         # Git configuration
├── collect.py                         # Convenience wrapper
├── train_models.py                    # Model training script
├── test_dashboard.py                  # Dashboard validation
└── setup.py                           # Installation script (optional)
```

## Installation

### Prerequisites

- Python 3.13 or higher
- macOS, Linux, or Windows
- TomTom API key ([get here](https://developer.tomtom.com/))
- OpenWeather API key ([get here](https://openweathermap.org/api))

### Quick Start

#### 1. Clone & Setup

```bash
cd urban-mobility-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# TOMTOM_API_KEY=your_key_here
# OPENWEATHER_API_KEY=your_key_here
```

#### 3. Verify Installation

```bash
python test_dashboard.py
# Expected: ✓ All tests passed!
```

#### 4. Start Collecting Data

```bash
# Single collection cycle
python -m src.route_extraction

# Continuous collection (every 120 seconds)
python -m src.route_extraction --interval 120
```

#### 5. Train Prediction Models

```bash
python train_models.py
# Trains travel time models for all routes with sufficient data
```

#### 6. Launch Dashboard

```bash
python -m streamlit run streamlit_app/app.py
# Opens http://localhost:8501
```

## Routes Monitored

| Origin | Destination | Distance | Typical Time |
|--------|-------------|----------|--------------|
| Msida  | Gzira       | 1.5 km   | ~5 min       |
| Msida  | Sliema      | 2.2 km   | ~6 min       |
| Msida  | Valletta    | 2.5 km   | ~10 min      |
| Msida  | St Julian's | 1.8 km   | ~10 min      |
| Msida  | Birkirkara  | 4.1 km   | ~8 min       |
| Msida  | Marsaskala  | 12.7 km  | ~19 min      |

To add new routes, edit `src/locations.py`:

```python
LOCATIONS = {
    "Valletta": (35.8989, 14.5146),
    "Your Location": (lat, lon),  # Add here
}

ROUTES = [
    ("Msida", "Your Location"),  # Add route here
]
```

## Usage

### Command Line Interface

```bash
# Single data collection
python -m src.route_extraction

# Continuous collection every 120 seconds
python -m src.route_extraction --interval 120

# Help
python -m src.route_extraction --help
```

### Data Migration

Import historical CSV data to SQLite:

```bash
# Preview what would be imported
python -m src.migration --dry-run

# Perform migration
python -m src.migration --skip-confirmation
```

### Historical Analysis

Analyze trends and patterns:

```bash
# Summary report for all routes
python -m src.analytics summary

# Route trend analysis (increasing/decreasing/stable)
python -m src.analytics trend Msida Gzira

# Weather impact on travel times
python -m src.analytics weather Msida Sliema

# Route reliability score (0-100%)
python -m src.analytics consistency Msida Valletta

# Compare all routes
python -m src.analytics compare --hours 24
```

### Model Training

Train travel time prediction models:

```bash
# Train all routes with sufficient data
python train_models.py

# View model status
python -m src.predictor status Msida Marsaskala
```

### Dashboard

Launch the interactive Streamlit dashboard:

```bash
python -m streamlit run streamlit_app/app.py

# Custom port
python -m streamlit run streamlit_app/app.py --server.port 8502
```

**Dashboard Features**:
- 🎯 Route selector with dynamic data
- 📅 Time range filters (24h, 7d, 30d, custom)
- 📊 Real-time metrics (travel time, delay, congestion)
- 🗺️ Interactive map with origin/destination
- 📈 Historical charts (travel time, traffic, weather)
- 📊 Route rankings and comparisons
- ⚠️ Smart alerts (high delay, stale data)
- 📥 Export to CSV/JSON

## Database

### SQLite Structure

**Primary database**: `data/mobility.db`

**Main table**: `route_measurements`

| Column | Type | Index | Description |
|--------|------|-------|-------------|
| id | INTEGER | PRIMARY | Auto-increment ID |
| timestamp | TEXT | ✓ | UTC ISO 8601 |
| origin | TEXT | ✓ | Route start |
| destination | TEXT | ✓ | Route end |
| distance_km | REAL | | Route distance |
| travel_time_min | REAL | | Current travel time |
| no_traffic_time_min | REAL | | Travel time without traffic |
| traffic_delay_min | REAL | | Traffic delay |
| traffic_length_km | REAL | | Length affected by traffic |
| average_speed_kmh | REAL | | Average speed |
| departure_time | TEXT | | Estimated departure (ISO) |
| arrival_time | TEXT | | Estimated arrival (ISO) |
| temperature | REAL | | Origin temperature (°C) |
| feels_like | REAL | | Origin "feels like" (°C) |
| humidity | REAL | | Origin humidity (%) |
| weather | TEXT | | Weather description |
| polyline | TEXT | | Route geometry (JSON) |
| created_at | TEXT | | Record creation time |

### CSV Backup

**Location**: `data/raw/route_weather_data.csv`

Maintains all historical records in CSV format for:
- Data portability
- External analysis
- Disaster recovery

## Predictive Models

### Architecture

Models are trained using **Random Forest Regression** (scikit-learn) with features:

- **Temporal**: Hour of day, day of week
- **Weather**: Temperature, humidity
- **Historical**: Average travel time (5-record rolling window)
- **Route**: Travel time without traffic

### Training

Minimum 50 samples per route (configurable):

```bash
python train_models.py
```

**Current Status**:
- ✅ Msida → Marsaskala (60 samples)
- ⏳ Others (need 50+ samples)

### Prediction

Models predict travel time with confidence scores:

```python
from src.predictor import RoutePredictor

predictor = RoutePredictor(db_path, models_dir)
time, confidence = predictor.predict_travel_time(
    "Msida", "Marsaskala",
    current_temp=25.0,
    current_humidity=70,
    no_traffic_time=18.3
)
# Returns: (19.2, 85.5) → 19.2 min @ 85.5% confidence
```

## Monitoring & Logs

### Application Logs

```bash
tail -f logs/collector.log
```

**Log Format**:
```
2026-07-19 00:48:54 - INFO - Starting collection cycle
2026-07-19 00:48:55 - INFO - Msida→Gzira: 4.9min (+0.0min delay)
2026-07-19 00:48:57 - INFO - Saved 6 records to CSV
2026-07-19 00:48:57 - INFO - Saved 6 records to SQLite
```

### Database Queries

```bash
# Total records
sqlite3 data/mobility.db "SELECT COUNT(*) FROM route_measurements;"

# Records per route
sqlite3 data/mobility.db "SELECT origin, destination, COUNT(*) FROM route_measurements GROUP BY origin, destination;"

# Latest measurement
sqlite3 data/mobility.db "SELECT timestamp, origin, destination, travel_time_min FROM route_measurements ORDER BY timestamp DESC LIMIT 1;"
```

## Security

### API Keys

- ✅ Never committed (`.env` in `.gitignore`)
- ✅ Loaded from environment only
- ✅ Never logged or printed
- ✅ Validated at startup

### Data

- ✅ Local-only by default
- ✅ No PII collected
- ✅ UNIQUE constraints prevent duplicates
- ✅ Transactions ensure consistency

### Deployment Checklist

Before deploying to production:

- [ ] Generate new API keys in secure environment
- [ ] Update `.env` (never commit)
- [ ] Test with `python test_dashboard.py`
- [ ] Verify logs don't contain sensitive data
- [ ] Set up automated backup of SQLite database
- [ ] Configure log rotation
- [ ] Monitor disk space for `data/` directory

## Performance Tips

### For Faster Queries

```python
# Use hour-based aggregation
analytics.get_hourly_statistics("Msida", "Gzira", days=7)

# Limit data range
db.query_measurements(origin, destination, hours=24, limit=1000)
```

### For Production

- Use systemd to auto-restart collector
- Run dashboard on separate port
- Archive logs weekly
- Back up SQLite monthly
- Monitor memory (collector + Streamlit)

## Troubleshooting

### "Missing TOMTOM_API_KEY"

```bash
# Verify .env exists
cat .env

# Should show:
# TOMTOM_API_KEY=your_key
# OPENWEATHER_API_KEY=your_key
```

### No Data in Database

Check logs:
```bash
tail -50 logs/collector.log
```

**Common causes**:
- Invalid API keys (check responses)
- Network connectivity (firewall?)
- API rate limits (wait 60 seconds)
- Coordinates outside service area

### Dashboard Errors

```bash
# Test components
python test_dashboard.py

# Check Streamlit logs
python -m streamlit run streamlit_app/app.py 2>&1 | tail -20
```

### Model Training Fails

```bash
# Verify data quality
python -m src.analytics summary

# Check sample counts per route
# Models need minimum 50 samples (configurable)
```

## API Reference

### TomTom Routing API

Calculates routes with traffic data:
- Distance (meters → km)
- Travel time with traffic (seconds → minutes)
- Travel time without traffic (seconds → minutes)
- Polyline geometry (optional)

### OpenWeather Current API

Fetches real-time weather:
- Temperature (°C)
- Feels like (°C)
- Humidity (%)
- Weather description

### Database API

```python
from src.database import RouteDatabase

db = RouteDatabase(csv_path, db_path)

# Query with filters
df = db.query_measurements(
    origin="Msida",
    destination="Gzira",
    start_timestamp="2026-07-19T00:00:00+00:00",
    end_timestamp="2026-07-19T23:59:59+00:00",
    limit=1000
)

# Get statistics
stats = db.get_route_statistics("Msida", "Gzira", hours=24)

# Export
db.export_route_data("Msida", "Gzira", Path("export.csv"))
```

## Roadmap

### Completed ✅

- [x] Phase 1: Modular collector with retries & logging
- [x] Phase 2: SQLite migration & historical analysis
- [x] Phase 3: Professional Streamlit dashboard
- [x] Phase 4: Prediction models & documentation

### Future Enhancements

- [ ] Web API (FastAPI) for programmatic access
- [ ] Real-time notifications (Slack, email)
- [ ] Advanced forecasting (ARIMA, Prophet)
- [ ] Mobile app (React Native)
- [ ] Cloud deployment (AWS, Google Cloud)
- [ ] Multi-city expansion
- [ ] Traffic pattern clustering (k-means)

## Contributing

To extend this project:

1. **Add new routes**: Edit `src/locations.py`
2. **Add new metrics**: Extend `database.py` schema
3. **Improve predictions**: Train in `src/models/travel_time_model.py`
4. **Enhance dashboard**: Add components in `streamlit_app/components.py`

## Testing

```bash
# Run all tests
python tests/test_locations.py
python tests/test_database.py
python tests/test_analytics.py

# Test dashboard
python test_dashboard.py

# Manual testing
python -m src.route_extraction
python -m streamlit run streamlit_app/app.py
```

## License

Internal use. Do not redistribute without permission.

## Support

For issues:

1. Check logs: `tail logs/collector.log`
2. Verify APIs: TomTom & OpenWeather dashboards
3. Test components: `python test_dashboard.py`
4. Review error messages in console

## Citation

If you use this project in research or publications, please cite:

```bibtex
@software{urban_mobility_2026,
  title={Urban Mobility Analytics},
  author={Your Name},
  year={2026},
  url={https://github.com/username/urban-mobility-analytics}
}
```

---

**Last Updated**: 2026-07-19  
**Maintainer**: Your Name  
**Status**: Production-Ready ✅  
**Python**: 3.13+  
**License**: Internal Use
