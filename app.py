"""FastAPI backend + serves the frontend. Run: uvicorn app:app --reload"""
import json, sqlite3
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from src import pipeline, predict

ROOT = Path(__file__).parent
app = FastAPI(title="Customer Churn Pipeline API")

class Customer(BaseModel):
    age: float = Field(ge=18, le=100); gender: str = "M"; tenure_months: int = Field(ge=1)
    plan: str = "Basic"; monthly_minutes: float = Field(ge=0); data_gb: float = Field(ge=0)
    support_calls: int = Field(ge=0); monthly_charges: float = Field(ge=0)
    late_payments: int = Field(ge=0); logins: int = Field(ge=0); errors: int = Field(ge=0)

@app.on_event("startup")
def boot():
    if not (ROOT/"models"/"model.pkl").exists(): pipeline.run()

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.get("/api/metrics")
def metrics(): return json.loads((ROOT/"models"/"metrics.json").read_text())

@app.post("/api/predict")
def predict_one(c: Customer): return predict.predict_one(c.model_dump())

@app.post("/api/run-pipeline")
def run_pipeline(): return pipeline.run()

@app.get("/api/quality")
def quality(): return pd.read_csv(ROOT/"output"/"quality_report.csv").fillna("").to_dict("records")

@app.get("/api/predictions")
def predictions(risk: str = "", limit: int = 50):
    q, args = "SELECT * FROM predictions", []
    if risk:
        if risk not in ("Low", "Medium", "High"): raise HTTPException(400, "bad risk")
        q += " WHERE risk=?"; args.append(risk)
    q += " ORDER BY churn_probability DESC LIMIT ?"; args.append(min(limit, 500))
    with sqlite3.connect(ROOT/"database"/"customer.db") as con:
        rows = pd.read_sql(q, con, params=args)
        counts = pd.read_sql("SELECT risk, COUNT(*) n FROM predictions GROUP BY risk", con)
    return {"rows": rows.to_dict("records"), "summary": dict(zip(counts.risk, counts.n))}

app.mount("/static", StaticFiles(directory=ROOT/"frontend"), name="static")

@app.get("/")
def index(): return FileResponse(ROOT/"frontend"/"index.html")
