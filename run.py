import subprocess
import time
import webbrowser

# Start FastAPI
backend = subprocess.Popen(
    [
        "python",
        "backend/app.py"
    ]
)

time.sleep(3)

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