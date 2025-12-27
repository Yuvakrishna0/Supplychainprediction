# serve/serve_model.py
from fastapi import FastAPI
import joblib, os, numpy as np, uvicorn
from pydantic import BaseModel

MODEL_PATH = "models/model.xgb"

app = FastAPI()

class InputItem(BaseModel):
    gdelt_tone_mean: float
    gdelt_tone_std: float
    port_congestion_z: float

@app.on_event("startup")
def load_model():
    global model
    model = joblib.load(MODEL_PATH)

@app.post("/predict")
def predict(item: InputItem):
    X = np.array([[item.gdelt_tone_mean, item.gdelt_tone_std, item.port_congestion_z]])
    p = model.predict_proba(X)[0,1]
    return {"risk_p": float(p)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
