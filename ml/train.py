import csv
import sys
from pathlib import Path
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA_PATH = ROOT / "data" / "dataset.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "nn_model.npz"

from nn_numpy import init_params, forward, compute_loss, backward, update_params, predict

FEATURE_COLS = [
    "tire_wear", "laps_since_pit", "recent_pace_drop",
    "gap_ahead", "gap_behind", "traffic_density",
    "is_stuck", "lap_norm", "safety_car_active"
]

def load_data(path):
    rows = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            x = [float(r[c]) for c in FEATURE_COLS]
            y = int(r["label"])
            rows.append((x, y))
    X = np.array([r[0] for r in rows], dtype=np.float64)
    y = np.array([r[1] for r in rows], dtype=np.float64).reshape(-1, 1)
    return X, y

def train_val_split(X, y, val_ratio=0.2, seed=42):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(X))
    rng.shuffle(idx)
    n_val = int(len(X) * val_ratio)
    val_idx, tr_idx = idx[:n_val], idx[n_val:]
    return X[tr_idx], y[tr_idx], X[val_idx], y[val_idx]

def normalize_fit(X):
    mean = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True) + 1e-8
    return mean, std

def normalize_apply(X, mean, std):
    return (X - mean) / std

def accuracy(y_pred, y_true):
    return (y_pred == y_true).mean()

def iterate_minibatches(X, y, batch_size=64, seed=42):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(X))
    rng.shuffle(idx)
    for s in range(0, len(X), batch_size):
        b = idx[s:s+batch_size]
        yield X[b], y[b]


def save_model(path, params, mean, std, feature_cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        W1=params["W1"],
        b1=params["b1"],
        W2=params["W2"],
        b2=params["b2"],
        W3=params["W3"],
        b3=params["b3"],
        mean=mean,
        std=std,
        feature_cols=np.array(feature_cols),
    )

def main():
    X, y = load_data(DATA_PATH)
    X_tr, y_tr, X_val, y_val = train_val_split(X, y)

    mean, std = normalize_fit(X_tr)
    X_tr = normalize_apply(X_tr, mean, std)
    X_val = normalize_apply(X_val, mean, std)

    params = init_params(n_x=9, n_h1=16, n_h2=8, seed=42)

    lr = 0.01
    epochs = 150
    batch_size = 64

    for epoch in range(1, epochs + 1):
        for Xb, yb in iterate_minibatches(X_tr, y_tr, batch_size=batch_size, seed=epoch):
            y_hat, cache = forward(Xb, params)
            grads = backward(params, cache, yb)
            params = update_params(params, grads, lr=lr)

        if epoch % 10 == 0 or epoch == 1:
            tr_hat, _ = forward(X_tr, params)
            va_hat, _ = forward(X_val, params)
            tr_loss = compute_loss(tr_hat, y_tr)
            va_loss = compute_loss(va_hat, y_val)
            va_pred = predict(X_val, params, threshold=0.5)
            va_acc = accuracy(va_pred, y_val)
            print(f"Epoch {epoch:03d} | train_loss={tr_loss:.4f} val_loss={va_loss:.4f} val_acc={va_acc:.4f}")

    save_model(MODEL_PATH, params, mean, std, FEATURE_COLS)
    print(f"\nSaved model to: {MODEL_PATH}")

if __name__ == "__main__":
    main()