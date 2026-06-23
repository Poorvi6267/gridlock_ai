import subprocess
import time
import webbrowser
import requests

# Start FastAPI
backend = subprocess.Popen(
    [
        "python",
        "backend/app.py"
    ]
)

for _ in range(20):

    try:

        r = requests.get(
            "http://127.0.0.1:8000/health",
            timeout=1
        )

        if r.status_code == 200:
            break

    except Exception:
        pass

    time.sleep(1)

# Start Streamlit
frontend = subprocess.Popen(
    [
        "streamlit",
        "run",
        "frontend/dashboard.py"
    ]
)

time.sleep(5)

webbrowser.open(
    "http://localhost:8501"
)

backend.wait()
frontend.wait()