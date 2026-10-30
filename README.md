# Customer Churn Pipeline

An end-to-end machine learning pipeline that predicts customer churn, with a FastAPI backend, a web dashboard and Docker deployment.

## Project Structure

```
customer_churn_pipeline/
├── data/
│   ├── customers.csv
│   ├── usage.csv
│   ├── transactions.csv
│   ├── customer_logs.txt
│   └── products.json
├── src/
│   ├── ingestion.py
│   ├── validation.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── train.py
│   ├── predict.py
│   └── pipeline.py
├── models/
│   ├── model.pkl
│   └── preprocessing.pkl
├── output/
│   ├── quality_report.csv
│   ├── anomalies.csv
│   ├── features.csv
│   └── predictions.csv
├── database/
│   └── customer.db
├── frontend/
│   └── index.html
├── app.py
├── Dockerfile
├── render.yaml
├── README.md
└── requirements.txt
```

Extra files beyond the core structure: `src/generate_data.py` (creates sample data), `models/metrics.json` (model scores), and `app.py` + `frontend/` (backend and UI).

## Pipeline Stages

| Stage | File | What it does |
|---|---|---|
| Ingestion | `src/ingestion.py` | Loads CSV, TXT and JSON sources and merges them on `customer_id` |
| Validation | `src/validation.py` | Writes `quality_report.csv` (missing values, types) and `anomalies.csv` (negatives, outliers) |
| Cleaning | `src/cleaning.py` | Removes duplicates, fixes invalid values, fills missing data |
| Feature Engineering | `src/feature_engineering.py` | Builds derived features and the scaling/encoding preprocessor |
| Training | `src/train.py` | Trains a Random Forest, saves `model.pkl` and `preprocessing.pkl` |
| Prediction | `src/predict.py` | Scores customers with churn probability and Low/Medium/High risk |
| Orchestration | `src/pipeline.py` | Runs every stage, writes `output/` files and `database/customer.db` |

## Quick Start

```bash
git clone https://github.com/<your-username>/customer_churn_pipeline.git
cd customer_churn_pipeline
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.pipeline           # run the full pipeline
uvicorn app:app --reload         # start API + dashboard
```

Open http://localhost:8000 for the dashboard and http://localhost:8000/docs for the API docs.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/metrics` | Model accuracy, F1, ROC-AUC |
| GET | `/api/quality` | Data quality report |
| GET | `/api/predictions?risk=High` | Predictions, optionally filtered by risk |
| POST | `/api/predict` | Predict churn for one customer |
| POST | `/api/run-pipeline` | Re-run the whole pipeline |

## Deployment

**Docker**
```bash
docker build -t churn-pipeline .
docker run -p 8000:8000 churn-pipeline
```

**Render (free tier):** push to GitHub, then in Render choose New → Blueprint and select this repo. `render.yaml` configures everything.

**Railway / Fly.io / Google Cloud Run:** deploy directly from the `Dockerfile`; the app reads the `$PORT` variable.

## Using Your Own Data

Replace the files in `data/` keeping the same column names, then run `python -m src.pipeline` or call `POST /api/run-pipeline`.

## Tech Stack

Python, pandas, scikit-learn, FastAPI, SQLite, Docker, HTML/CSS/JavaScript.
