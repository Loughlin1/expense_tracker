import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from lightgbm import LGBMClassifier


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["Date", "Name", "Amount", "Notes and #tags", "Category"])
    return df


def preprocess_data(df: pd.DataFrame):
    # Label encode the target category
    label_encoder = LabelEncoder()
    df["CategoryEncoded"] = label_encoder.fit_transform(df["Category"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["DayOfWeek"] = df["Date"].dt.dayofweek  # Monday=0, Sunday=6
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    return df, label_encoder


def build_preprocessor():
    # Combine TF-IDF on description and passthrough for amount
    preprocessor = ColumnTransformer(
        transformers=[
            ("name", TfidfVectorizer(max_features=200), "Name"),
            ("notes", TfidfVectorizer(max_features=300), "Notes and #tags"),
            ("amount", "passthrough", ["Amount"]),
            (
                "date_features",
                OneHotEncoder(handle_unknown="ignore"),
                ["DayOfWeek", "Month", "Day"],
            ),
            ("account_encoded", OneHotEncoder(), ["Account"]),
        ]
    )
    return preprocessor


def train_model(
    df: pd.DataFrame, features: list, target: str, preprocessor, label_encoder
):
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    # Fit transform on training data
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Train classifier
    model = LGBMClassifier()
    model.fit(X_train_transformed, y_train)

    # Predict & evaluate
    y_pred = model.predict(X_test_transformed)

    unique_labels = np.unique(y_test)
    print("Classification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=unique_labels,
            target_names=label_encoder.inverse_transform(unique_labels),
        )
    )

    return model, preprocessor


def predict(model, preprocessor, label_encoder, new_data: pd.DataFrame):
    X_new = preprocessor.transform(new_data)
    preds = model.predict(X_new)
    return label_encoder.inverse_transform(preds)


# === RUN SCRIPT ===
if __name__ == "__main__":
    import os
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    DATA_DIR = config["data_dir"]
    path = os.path.join(DATA_DIR, "transactions_labelled.csv")

    # Load and prepare
    df = load_data(path)
    df, label_encoder = preprocess_data(df)
    preprocessor = build_preprocessor()
    print(df.columns)
    features = [
        "Name",
        "Amount",
        "Amount Out",
        "Amount In",
        "Notes and #tags",
        "Account",
        "DayOfWeek",
        "Month",
        "Day",
    ]
    target = "CategoryEncoded"

    # Train
    model, preprocessor = train_model(df, features, target, preprocessor, label_encoder)

# Save after training
with open("models/expense_classifier.pkl", "wb") as f:
    pickle.dump((model, preprocessor, label_encoder), f)

# Later, load and predict
with open("models/expense_classifier.pkl", "rb") as f:
    model, preprocessor, label_encoder = pickle.load(f)

# Predict on new data
new_transactions = pd.DataFrame(
    [
        {
            "Name": "Tesco Supermarket",
            "Amount": 54.23,
            "Notes and #tags": "",
            "Account": "Monzo",
            "DayOfWeek": 3,
            "Month": 7,
            "Day": 16,
        },
        {
            "Name": "Uber trip",
            "Amount": 12.80,
            "Notes and #tags": "",
            "Account": "Lloyds",
            "DayOfWeek": 2,
            "Month": 7,
            "Day": 15,
        },
    ]
)

X_new = preprocessor.transform(new_transactions)
preds_encoded = model.predict(X_new)
preds = label_encoder.inverse_transform(preds_encoded)
print(preds)
