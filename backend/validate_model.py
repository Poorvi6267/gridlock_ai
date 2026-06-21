from ml_engine import predict_all

sample = {
    "event_type": "planned",
    "event_cause": "accident",
    "veh_type": "car",

    "corridor": "Mysore Road",
    "zone": "South Zone 1",
    "junction": "Kengeri",

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

print(predict_all(sample))