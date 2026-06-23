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

# ✅ CHANGE 1: Health-check poll replaces time.sleep(3)
# ❌ OLD: time.sleep(3) — fixed delay was a guess;
#         on slow machines models take longer to load
#         and the browser opened before server was ready
for _ in range(30):

    try:

        r = requests.get(
            "http://127.0.0.1:8000/health",
            timeout=1
        )

        if r.status_code == 200:
            print("✅ Backend ready")
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

# ✅ CHANGE 1 (continued): Poll Streamlit too
# ❌ OLD: time.sleep(5) — same problem as above
for _ in range(30):

    try:

        r = requests.get(
            "http://localhost:8501",
            timeout=1
        )

        if r.status_code == 200:
            print("✅ Frontend ready")
            break

    except Exception:
        pass

    time.sleep(1)

webbrowser.open("http://localhost:8501")

backend.wait()
frontend.wait()
