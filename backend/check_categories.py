# backend/check_categories.py

import joblib

model = joblib.load(
    "backend/models/duration_model.pkl"
)

encoder = model.named_steps["prep"]\
               .named_transformers_["cat"]

print(encoder.categories_)