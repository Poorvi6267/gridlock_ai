import joblib

duration = joblib.load(
    "backend/models/duration_model.pkl"
)

closure = joblib.load(
    "backend/models/closure_model.pkl"
)

tii = joblib.load(
    "backend/models/tii_model.pkl"
)

print(type(duration))
print(type(closure))
print(type(tii))

print("SUCCESS")