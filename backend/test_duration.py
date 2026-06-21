import joblib

model = joblib.load(
    "backend/models/duration_model.pkl"
)

payload = [[
    0,0,0,
    0,0,0,
    12.97,
    77.59,
    18,
    1,
    6,
    0,
    1,
    5,
    70,
    50,
    10,
    30,
    20,
    45,
    40
]]

print(model)