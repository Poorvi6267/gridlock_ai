import joblib

model = joblib.load(
    "backend/models/duration_model.pkl"
)

print(type(model))

print("\n========================")
print(model.named_steps.keys())
print("========================\n")

print(model.named_steps["prep"])

print("\n========================")
print(model.named_steps["prep"].transformers_)
print("========================")