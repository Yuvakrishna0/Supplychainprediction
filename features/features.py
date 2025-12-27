# features/build_features.py
import os, pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

def fetch_raw_events(limit_days=30):
    engine = create_engine(DATABASE_URL)
    q = text("SELECT * FROM raw_events WHERE event_time >= now() - interval '30 days';")
    return pd.read_sql(q, engine)

def aggregate_daily(df):
    df['ds'] = pd.to_datetime(df['event_time']).dt.date
    agg = df.groupby('ds').agg(
        gdelt_tone_mean=('AvgTone','mean'),
        gdelt_tone_std=('AvgTone','std'),
        event_count=('AvgTone','count')
    ).reset_index().fillna(0)
    # add port congestion if you have port data; else simulate
    import numpy as np
    agg['port_congestion_z'] = (agg['event_count'] - agg['event_count'].mean()) / (agg['event_count'].std() + 1e-6)
    return agg

def save_features(df):
    engine = create_engine(DATABASE_URL)
    df.to_sql("features_daily", engine, if_exists="replace", index=False)

def run_build():
    raw = fetch_raw_events()
    feats = aggregate_daily(raw)
    save_features(feats)
    print("Saved features:", feats.shape)

if __name__ == "__main__":
    run_build()
