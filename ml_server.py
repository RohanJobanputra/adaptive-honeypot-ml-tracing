from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load model & columns
model = joblib.load("bot_detection_model.joblib")
feature_columns = joblib.load("feature_columns.joblib")


class InputData(BaseModel):
    userAgent_len: int
    ua_bot_keyword: int
    referrer_present: int
    night_activity: int
    ip_freq: int
    uid_freq: int


@app.post("/predict")
def predict(data: InputData):
    df = pd.DataFrame([data.dict()])
    df = df.reindex(columns=feature_columns, fill_value=0)

    prediction = model.predict(df)[0]

    # Try to return a useful bot score (probability) if the model supports it
    score = None
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(df)[0]
            # assume positive class (bot) is at index 1
            score = float(proba[1])
        else:
            # fallback: just use the raw prediction as a simple score
            score = float(prediction)
    except Exception:
        score = float(prediction)

    return {
        "label": "bot" if prediction == 1 else "human",
        "score": score,
    }
