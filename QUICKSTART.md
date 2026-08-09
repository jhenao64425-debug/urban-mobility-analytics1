# Quick Start Guide 🚀

Get Urban Mobility Analytics up and running in 5 minutes.

## 1. Clone & Enter Directory

```bash
cd urban-mobility-analytics
```

## 2. Run Automatic Setup

```bash
bash setup_env.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create `.env` file
- Create necessary directories
- Validate setup with tests

## 3. Configure API Keys

Edit `.env` with your TomTom and OpenWeather API keys:

```bash
nano .env
```

Add:
```
TOMTOM_API_KEY=your_tomtom_key
OPENWEATHER_API_KEY=your_openweather_key
```

## 4. Start Collecting Data (Terminal 1)

```bash
# Collect data every 120 seconds
python -m src.route_extraction --interval 120
```

You should see output like:
```
✓ API keys validated
✓ Starting collection cycle
  Msida→Gzira: 4.9min (+0.0min delay)
  Msida→Sliema: 6.2min (+0.0min delay)
  ...
```

## 5. Train Prediction Models (Terminal 2)

Once you have 50+ records per route, train models:

```bash
python train_models.py
```

## 6. Launch Dashboard (Terminal 3)

```bash
python -m streamlit run streamlit_app/app.py
```

Opens automatically at `http://localhost:8501`

## Dashboard Features

- **Route Selector**: Choose from 6 pre-configured routes
- **Time Filters**: 24h, 7d, 30d, or custom date range
- **Live Metrics**: Travel time, delay, congestion, weather
- **Interactive Map**: Origin, destination, route visualization
- **Historical Charts**: 4 tabs of analysis & trends
- **Data Export**: Download as CSV or JSON
- **Route Rankings**: Compare all routes

## Common Commands

```bash
# View data summary
python -m src.analytics summary

# Analyze a specific route
python -m src.analytics trend Msida Marsaskala

# Check model status
python train_models.py

# Stop data collection
pkill -f "route_extraction"
```

## Troubleshooting

**Missing API keys?**
```bash
cat .env
# Should show your keys, not "your_key_here"
```

**No data in dashboard?**
```bash
# Check collector is running
ps aux | grep route_extraction

# View logs
tail -20 logs/collector.log
```

**Dashboard won't load?**
```bash
# Test components
python test_dashboard.py

# Check Streamlit
python -m streamlit run streamlit_app/app.py --logger.level=error
```

## Next Steps

1. Let collector run for 24+ hours to accumulate data
2. Train prediction models: `python train_models.py`
3. Integrate into your monitoring system
4. Read [README_FINAL.md](README_FINAL.md) for advanced features

## Architecture Overview

```
TomTom/OpenWeather APIs
         ↓
Collector (Python)
    ↓        ↓
   CSV     SQLite
         ↓
  Analytics Engine
    ├─ Historical Analysis
    ├─ Predictions (ML)
    └─ Dashboard (Streamlit)
```

## Support

- **Logs**: `tail -f logs/collector.log`
- **Database**: `sqlite3 data/mobility.db`
- **Documentation**: See README_FINAL.md
- **Issues**: Check GitHub issues or email support

---

**Time to first data**: ~2 minutes ⏱️  
**Time to dashboard**: ~5 minutes 📊  
**Time to predictions**: ~30 minutes (depends on data) 🤖

Happy tracking! 🚗
