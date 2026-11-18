"""Zadanie 2: trening modelu (Pipeline: StandardScaler + LogisticRegression) i zapis do models/."""
import os

import joblib
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from data_prep import DATA_PATH, RANDOM_SEED, load_data, split_data

# Zadanie 4: hiperparametry i ścieżka modelu z pliku .env
load_dotenv()
MAX_ITER = int(os.getenv("MAX_ITER", 1000))
C = float(os.getenv("C", 1.0))                  # odwrotność siły regularyzacji
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.joblib")
# Lab 5: powtarzana walidacja krzyżowa przed treningiem (0 = pomiń)
CV_REPEATS = int(os.getenv("CV_REPEATS", 0))
N_JOBS = int(os.getenv("N_JOBS", 1))           # liczba procesów joblib (-1 = wszystkie rdzenie)


def build_pipeline():
    """Pipeline: skalowanie cech + regresja logistyczna (jak w lab. 2)."""
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=C, max_iter=MAX_ITER, random_state=RANDOM_SEED)),
        ]
    )


def train(X_train, y_train):
    """Uczy pipeline na zbiorze treningowym i zwraca wytrenowany model."""
    model = build_pipeline()
    model.fit(X_train, y_train)                 # scaler.fit + clf.fit w jednym wywołaniu
    return model


def cross_validate(X, y, repeats=CV_REPEATS):
    """Accuracy z powtarzanej 5-krotnej walidacji krzyżowej (repeats x 5 treningów)."""
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeats, random_state=RANDOM_SEED)
    return cross_val_score(build_pipeline(), X, y, cv=cv, n_jobs=N_JOBS)


def save_model(model, path=MODEL_PATH):
    """Zapisuje model w formacie .joblib (tworzy katalog, jeśli nie istnieje)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    joblib.dump(model, path)


if __name__ == "__main__":
    df = load_data(DATA_PATH)
    X_train, X_test, y_train, y_test = split_data(df)
    if CV_REPEATS > 0:
        scores = cross_validate(X_train, y_train)
        print(f"Walidacja krzyżowa 5x{CV_REPEATS}: accuracy {scores.mean():.4f} ± {scores.std():.4f}")
    model = train(X_train, y_train)
    save_model(model)
    print(f"Wytrenowano model na {len(X_train)} próbkach, zapisano do {MODEL_PATH}")
