# AI-Powered IT Helpdesk Ticket Classifier

This project delivers a production-ready service that categorises incoming IT help-desk tickets ( _hardware issue_, _software bug_, _password reset_ ) and auto-assigns them to the correct team via a simple REST API.

---

## 1. Features

* **FastAPI** micro-service exposing `/classify` endpoint
* **Scikit-Learn** NLP pipeline (Tfidf + Logistic Regression)
* **Joblib** model persistence – model loads once, reused for all requests

---

## 2. Quick Start (Local)

```bash
# 1. Install dependencies (Python 3.9+) – ideally inside a venv
pip install -r requirements.txt

# 2. Prepare training data (CSV with columns: text,category)
#    Example rows:
#    "My laptop does not turn on","hardware issue"
#    "Reset my Active Directory password","password reset"
#    "App crashes when I click save","software bug"

# 3. Train the model (creates model/classifier.pkl)
python train_model.py --data tickets.csv

# 4. Start the API server
uvicorn app.main:app --reload --port 8000
```

Send a request:

```bash
curl -X POST http://localhost:8000/classify \
     -H "Content-Type: application/json" \
     -d '{"text":"My Outlook keeps asking for password"}'
```

Response:

```json
{
  "category": "password reset",
  "assigned_team": "IT Support Desk"
}
```

---


## 3. Endpoint Reference

| Method | Path       | Body (JSON)                | Response                                             |
|--------|------------|----------------------------|------------------------------------------------------|
| POST   | `/classify`| `{ "text": "<ticket>" }` | `{ "category": "...", "assigned_team": "..." }` |
| GET    | `/`        | –                          | `{ "status": "Ticket Classifier up and running" }` |

---

## 4. Project Structure

```
.
├── app/
│   └── main.py          # FastAPI application
├── model/               # Generated after training
├── train_model.py       # Training script
├── requirements.txt
└── README.md
```

---

## 5. Extending

* **More categories** – add labelled rows to `tickets.csv`, retrain.
* **Advanced models** – replace Logistic Regression with e.g. `sklearn.svm.SVC` or fine-tuned transformers (HuggingFace) for better accuracy.
* **CI/CD** – integrate training + deployment into your pipeline (GitHub Actions, Azure DevOps, etc.).

---

© 2024 IT Helpdesk AI – MIT License
