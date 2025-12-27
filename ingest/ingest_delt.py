"""
# ingest/ingest_gdelt.py
import os, time, requests
import pandas as pd
from io import StringIO
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")

def fetch_gdelt_recent(query="supply chain OR shipping OR logistics", maxrecords=500):
    url = f"https://api.gdeltproject.org/api/v2/events/doc/doc?query={requests.utils.quote(query)}&format=csv&maxrecords={maxrecords}&sort=DateDesc"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"GDELT fetch failed: {r.status_code}")
    df = pd.read_csv(StringIO(r.text))
    # keep columns we need
    cols = [c for c in ["SQLDATE","Actor1Name","Actor2Name","AvgTone","ActionGeo_CountryCode","EventRootCode","EventBaseCode","EventCode","SourceURL"] if c in df.columns]
    df = df[cols].copy()
    df["event_time"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d", errors="coerce")
    return df

def write_raw_events(df):
    engine = create_engine(DATABASE_URL)
    df.to_sql("raw_events", engine, if_exists="append", index=False)

def run_once():
    try:
        df = fetch_gdelt_recent()
    except Exception as e:
        print("GDELT failed, loading synthetic sample:", e)
        # fallback to synthetic sample generation
        dates = pd.date_range(datetime.utcnow()-pd.Timedelta(days=30), periods=30)
        df = pd.DataFrame({"SQLDATE": [d.strftime("%Y%m%d") for d in dates], "AvgTone": pd.np.random.normal(0, 3, len(dates)), "ActionGeo_CountryCode": ["USA"]*len(dates)})
        df["event_time"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")
    write_raw_events(df)
    print(f"Written {len(df)} raw events at {datetime.utcnow()}")

if __name__ == "__main__":
    # simple poller: run then sleep (if you use systemd or Replit schedule, remove loop)
    while True:
        run_once()
        time.sleep(60 * 15)  # poll every 15 minutes
""" 
from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_k5JYXPoFzM1N@ep-wandering-salad-a1c7264o-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

# Create a small sample table
data = {
    "ActionGeo_CountryCode": ["USA", "IND", "CHN", "BRA", "GBR"],
    "event_time": pd.date_range("2025-11-01", periods=5),
}
df = pd.DataFrame(data)
df.to_sql("raw_events", engine, if_exists="replace", index=False)
print("✅ raw_events table created successfully")
