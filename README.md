# Gridlock AI / TrafficSense

AI-powered traffic incident response and command center for Bengaluru traffic operations.

## Overview

This project predicts traffic incident severity, road closure probability, and expected duration, then turns those predictions into actionable recommendations such as resource deployment and diversion planning. The final results are displayed in a Streamlit dashboard.

The system is split into four parts:

- **Model generation**: `gridlock3.ipynb`
- **Backend API**: `backend/app.py`
- **Frontend dashboard**: `frontend/dashboard.py`
- **Launcher**: `run.py`

## How it works

1. `gridlock3.ipynb` processes the dataset and trains the models.
2. The notebook generates model files and supporting JSON files.
3. The FastAPI backend loads those files and exposes prediction endpoints.
4. The Streamlit UI sends incident data to the backend.
5. The backend returns predictions, resources, diversion recommendations, and route data.
6. The dashboard displays the final result in a command-center style UI.

## Main outputs

- **Predicted duration**
- **Road closure probability**
- **Traffic Impact Index (TII)**
- **Priority level**
- **Risk score**
- **Resource deployment plan**
- **Diversion strategy**
- **Route visualization**
- **Historical comparison**
- **Downloadable incident report**

## Repository structure

```text
backend/
  app.py
  ml_engine.py
  resource_engine.py
  diversion.py
  maps_engine.py
  models/
  data/

frontend/
  dashboard.py

gridlock3.ipynb
run.py
predictions.db
```

## Requirements

Install the Python packages listed in `requirements.txt`.

## Step-by-step setup

### 1. Create and activate a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate the model artifacts

Run the notebook `gridlock3.ipynb` first so the following files exist:

- `backend/models/duration_model.pkl`
- `backend/models/closure_model.pkl`
- `backend/models/tii_model.pkl`
- `backend/models/feature_columns.pkl`
- `backend/models/risk_scaler.pkl`
- `backend/data/corridor_risk.json`
- `backend/data/junction_risk.json`
- `backend/data/event_severity.json`

These files are required by the backend.

### 4. Start the application

Run the launcher:

```bash
python run.py
```

This starts both:
- FastAPI backend at `http://127.0.0.1:8000`
- Streamlit frontend at `http://localhost:8501`

### 5. Use the dashboard

Open the Streamlit app in your browser and:
- select an incident type
- choose corridor and junction
- set severity and traffic parameters
- click **Analyze Incident**

The dashboard will display predictions, resources, diversion routes, maps, and reports.

## API endpoints

### `GET /health`
Checks whether the backend is running.

### `GET /corridors`
Returns corridor names with normalized risk scores.

### `GET /junctions`
Returns junction names and coordinates.

### `GET /status`
Returns live incident KPIs from the SQLite log.

### `GET /history`
Returns historical average duration and total prediction count.

### `POST /predict`
Returns the combined ML prediction result.

### `POST /predict-duration`
Returns predicted duration only.

### `POST /predict-closure`
Returns road closure probability only.

### `POST /predict-tii`
Returns traffic impact index only.

### `POST /recommend`
Returns resource recommendations and diversion advice.

### `POST /route`
Returns route coordinates for map visualization.

## Notes

- The project is designed around historical Bengaluru traffic patterns.
- `gridlock3.ipynb` must be run before starting the backend if the model files are missing.
- The backend logs combined predictions to SQLite (`predictions.db`).
- SHAP is used for explainability when available; otherwise the system falls back to rule-based reasoning.

## License

Add your preferred license here.
