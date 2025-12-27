# train/train.py
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import mlflow, mlflow.sklearn
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBClassifier
from sklearn.metrics import average_precision_score, brier_score_loss

DATABASE_URL = os.getenv("DATABASE_URL")
MLFLOW_URI = f"https://dagshub.com/{os.getenv('DAGSHUB_USERNAME')}/supplychain-early-warning.mlflow"

def load_features():
    engine = create_engine(DATABASE_URL)
    q = text("SELECT * FROM features_daily ORDER BY ds;")
    return pd.read_sql(q, engine)

def prepare_data(feats):
    feats = feats.sort_values("ds")
    feats['label_bottleneck_next_14d'] = (feats['port_congestion_z'].shift(-7) > 1.0).astype(int)  # example label
    feats.dropna(inplace=True)
    X = feats[['gdelt_tone_mean','gdelt_tone_std','port_congestion_z']].values
    y = feats['label_bottleneck_next_14d'].values
    return X, y, feats

def train_and_log(X, y):
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("SupplyChainPrediction")
    tscv = TimeSeriesSplit(n_splits=3)
    scores = []
    for tr, te in tscv.split(X):
        m = XGBClassifier(n_estimators=200, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss')
        m.fit(X[tr], y[tr])
        p = m.predict_proba(X[te])[:,1]
        scores.append(average_precision_score(y[te], p))
    mean_score = np.mean(scores)
    # final model on all data
    final = XGBClassifier(n_estimators=300, learning_rate=0.04, use_label_encoder=False, eval_metric='logloss')
    final.fit(X, y)
    # log
    with mlflow.start_run():
        mlflow.log_metric("pr_auc_cv", float(mean_score))
        mlflow.sklearn.log_model(final, "xgb_model")
    return final

def save_model_local(model, path="models/model.xgb"):
    import joblib
    joblib.dump(model, path)

if __name__ == "__main__":
    feats = load_features()
    X, y, feats = prepare_data(feats)
    model = train_and_log(X, y)
    save_model_local(model)
    print("Training finished and model saved.")
