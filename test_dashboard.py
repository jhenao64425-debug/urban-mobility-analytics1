#!/usr/bin/env python
"""Test script to verify dashboard loads without errors."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all dashboard imports work."""
    try:
        from streamlit_app.components import (
            render_header,
            render_sidebar_filters,
            render_metric_cards,
            render_traffic_status,
            render_map,
            render_alerts,
            render_historical_table,
            render_export_buttons,
        )
        print("✓ Components imports OK")
        return True
    except Exception as e:
        print(f"✗ Components import error: {e}")
        return False


def test_database():
    """Test that database connection works."""
    try:
        from src.database import RouteDatabase
        from pathlib import Path

        db_path = Path(__file__).parent / "data" / "mobility.db"
        db = RouteDatabase(Path.home(), db_path)

        routes = db.get_available_routes()
        print(f"✓ Database OK - Found {len(routes)} routes")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_analytics():
    """Test that analytics module works."""
    try:
        from src.analytics import MobilityAnalytics
        from pathlib import Path

        db_path = Path(__file__).parent / "data" / "mobility.db"
        analytics = MobilityAnalytics(db_path)

        summary = analytics.db.get_database_summary()
        print(f"✓ Analytics OK - {summary['total_records']} total records")
        return True
    except Exception as e:
        print(f"✗ Analytics error: {e}")
        return False


def test_data_loading():
    """Test that data loads correctly."""
    try:
        from src.database import RouteDatabase
        from datetime import datetime, timezone, timedelta
        from pathlib import Path

        db_path = Path(__file__).parent / "data" / "mobility.db"
        db = RouteDatabase(Path.home(), db_path)

        routes = db.get_available_routes()
        if not routes:
            print("✗ No routes available")
            return False

        origin, destination = routes[0]
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=24)

        df = db.query_measurements(
            origin=origin,
            destination=destination,
            start_timestamp=start.isoformat(),
            end_timestamp=now.isoformat(),
        )

        print(f"✓ Data loading OK - Loaded {len(df)} records for {origin}→{destination}")
        return True
    except Exception as e:
        print(f"✗ Data loading error: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Urban Mobility Analytics Dashboard")
    print("=" * 50)

    tests = [
        ("Component Imports", test_imports),
        ("Database Connection", test_database),
        ("Analytics Module", test_analytics),
        ("Data Loading", test_data_loading),
    ]

    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 50)
    print("Summary:")
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("✓ All tests passed!" if all_passed else "✗ Some tests failed"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
