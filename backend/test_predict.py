from ml_engine import prepare_features

payload = {

    "event_type": 0,
    "event_cause": 0,
    "veh_type": 0,

    "corridor": 0,
    "zone": 0,
    "junction": 0,

    "latitude": 12.97,
    "longitude": 77.59,

    "hour": 18,
    "weekday": 1,
    "month": 6,

    "weekend": 0,
    "peak_hour": 1,

    "event_frequency_score": 5,

    "closure_risk": 70,
    "duration_risk": 50,

    "junction_count": 10,
    "junction_duration": 30,

    "corridor_count": 20,
    "corridor_duration": 45,

    "historical_impact": 40
}

X = prepare_features(payload)

print(X)

print("\nDTYPES")
print(X.dtypes)