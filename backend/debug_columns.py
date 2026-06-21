# backend/debug_columns.py

import joblib

cols = joblib.load("backend/models/feature_columns.pkl")

print(type(cols))
print(len(cols))

for c in cols:
    print(c)