import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# ✅ Step 1: Load dataset
df = pd.read_csv("data2.csv")   # <-- your dataset file

# ✅ Step 2: Features and target
X = df.drop("label", axis=1)
y = df["label"]

# ✅ Step 3: Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ✅ Step 4: Train model
model = RandomForestClassifier()
model.fit(X, y_encoded)

# ✅ Step 5: Save model, encoder, columns
pickle.dump(model, open("rfc.pkl", "wb"))
pickle.dump(le, open("label_encoder.pkl", "wb"))
pickle.dump(X.columns, open("model_columns.pkl", "wb"))

print("Training complete and files saved ✅")