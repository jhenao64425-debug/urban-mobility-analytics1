"""Silver layer: Cleaned and transformed data."""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import sqlite3


class SilverLayer:
    """
    Silver Layer: Data transformation and enrichment.
    - Cleans and standardizes data
    - Performs transformations
    - Calculates derived metrics
    - Stores cleaned data
    """

    def __init__(self, db_path: Path):
        """Initialize silver layer."""
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Create silver layer tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Cleaned measurements (silver)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS silver_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                travel_time_min REAL NOT NULL,
                no_traffic_time_min REAL,
                traffic_delay_min REAL,
                average_speed_kmh REAL,
                congestion_level TEXT,
                origin_temperature REAL,
                origin_humidity REAL,
                origin_weather TEXT,
                destination_temperature REAL,
                destination_humidity REAL,
                destination_weather TEXT,
                hour INTEGER,
                day_of_week INTEGER,
                day_of_month INTEGER,
                month INTEGER,
                is_peak_hour INTEGER,
                is_weekend INTEGER,
                transformation_timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, origin, destination)
            )
        """)

        # Route aggregations (hourly)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS silver_route_hourly (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                avg_travel_time REAL,
                median_travel_time REAL,
                std_travel_time REAL,
                min_travel_time REAL,
                max_travel_time REAL,
                sample_count INTEGER,
                avg_speed REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, origin, destination)
            )
        """)

        conn.commit()
        conn.close()

    def transform_bronze(self, bronze_df: pd.DataFrame) -> Dict:
        """
        Transform bronze data to silver.

        Args:
            bronze_df: Data from bronze layer

        Returns:
            Transformation summary
        """
        df = bronze_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # 1. Standardize column names
        df = df.rename(columns={
            'raw_timestamp': 'timestamp'
        })

        # 2. Calculate derived metrics
        df['traffic_delay_min'] = df['travel_time_min'] - df.get('no_traffic_time_min', df['travel_time_min'])
        df['traffic_delay_min'] = df['traffic_delay_min'].clip(lower=0)

        # 3. Classify congestion level
        def classify_congestion(delay):
            if pd.isna(delay):
                return 'unknown'
            if delay <= 1:
                return 'free_flow'
            elif delay <= 4:
                return 'moderate'
            else:
                return 'heavy'

        df['congestion_level'] = df['traffic_delay_min'].apply(classify_congestion)

        # 4. Add temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_peak_hour'] = (df['hour'].isin([7, 8, 9, 17, 18, 19])).astype(int)
        df['is_weekend'] = (df['day_of_week'].isin([5, 6])).astype(int)

        # 5. Store in silver
        df['transformation_timestamp'] = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        try:
            # Insert or replace
            df.to_sql('silver_measurements', conn, if_exists='append', index=False)
            conn.commit()
            inserted = len(df)
        except Exception as e:
            inserted = 0
            return {'error': str(e), 'inserted': 0}
        finally:
            conn.close()

        return {
            'status': 'success',
            'records_transformed': inserted,
            'mean_travel_time': float(df['travel_time_min'].mean()),
            'mean_delay': float(df['traffic_delay_min'].mean())
        }

    def aggregate_hourly(self) -> Dict:
        """Aggregate silver data to hourly summaries."""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT
                timestamp,
                origin,
                destination,
                AVG(travel_time_min) as avg_travel_time,
                MEDIAN(travel_time_min) as median_travel_time,
                STDDEV(travel_time_min) as std_travel_time,
                MIN(travel_time_min) as min_travel_time,
                MAX(travel_time_min) as max_travel_time,
                COUNT(*) as sample_count,
                AVG(average_speed_kmh) as avg_speed
            FROM silver_measurements
            GROUP BY strftime('%Y-%m-%d %H:00', timestamp), origin, destination
        """

        try:
            df = pd.read_sql_query(query, conn)
            df['created_at'] = datetime.utcnow().isoformat()

            cursor = conn.cursor()
            df.to_sql('silver_route_hourly', conn, if_exists='append', index=False)
            conn.commit()

            return {
                'status': 'success',
                'hourly_records_created': len(df)
            }
        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()

    def get_route_profile(self, origin: str, destination: str, days: int = 30) -> Dict:
        """Get silver-layer profile for a route."""
        conn = sqlite3.connect(self.db_path)

        query = f"""
            SELECT
                hour,
                day_of_week,
                AVG(travel_time_min) as avg_time,
                STDDEV(travel_time_min) as std_time,
                COUNT(*) as count
            FROM silver_measurements
            WHERE origin = ? AND destination = ?
            AND timestamp > datetime('now', '-{days} days')
            GROUP BY hour, day_of_week
        """

        try:
            df = pd.read_sql_query(query, conn, params=(origin, destination))
            return {
                'status': 'success',
                'route': f'{origin} -> {destination}',
                'days': days,
                'profiles': df.to_dict('records')
            }
        except Exception as e:
            return {'error': str(e)}
        finally:
            conn.close()
