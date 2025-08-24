from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import os
from transformers import pipeline
from fastapi.responses import Response

# Allow rollback to the lightweight legacy model without code edits
USE_LEGACY = os.getenv("USE_LEGACY", "0") == "1"

app = FastAPI(title="AI-Powered Ticket Classifier", version="0.1.0")

# Remove early static mount (moved to bottom)
MODEL_PATH = os.getenv("MODEL_PATH", "model/classifier.pkl")
CATEGORY_TO_TEAM = {
    "hardware issue": "Hardware Support Team",
    "software bug": "Software Engineering Team",
    "password reset": "IT Support Desk"
}

class Ticket(BaseModel):
    text: str

_classifier = None
LABELS = list(CATEGORY_TO_TEAM.keys())

def get_zero_shot():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _classifier

# Lazy-load model on first request
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train the model first.")
        _model = joblib.load(MODEL_PATH)
    return _model

@app.post("/classify")
async def classify_ticket(ticket: Ticket):
    """Classify incoming ticket text and return category & assigned team."""
    try:
        if USE_LEGACY:
            model = get_model()
            prediction = model.predict([ticket.text])[0]
        else:
            classifier = get_zero_shot()
            result = classifier(ticket.text, candidate_labels=LABELS)
            prediction = result["labels"][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    assignment = CATEGORY_TO_TEAM.get(prediction, "General IT Team")
    return {"category": prediction, "assigned_team": assignment}

@app.post("/classify_file")
async def classify_file(file: UploadFile = File(...)):
    """Accept a CSV file with a 'text' column, return list of predictions."""
    import pandas as pd
    try:
        df = pd.read_csv(file.file)
        if "text" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain a 'text' column")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")
    try:
        if USE_LEGACY:
            model = get_model()
            preds = model.predict(df["text"].tolist())
        else:
            classifier = get_zero_shot()
            preds = [
                classifier(text, candidate_labels=LABELS)["labels"][0]
                for text in df["text"].tolist()
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    df["category"] = preds
    df["assigned_team"] = df["category"].map(CATEGORY_TO_TEAM).fillna("General IT Team")
    return df.to_dict(orient="records")
 
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/@vite/client")
async def vite_dummy():
    return Response(content="", media_type="application/javascript")

# Mount static frontend last to avoid overriding API routes
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")