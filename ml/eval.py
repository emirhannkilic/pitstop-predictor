import numpy as np
from train import (
    load_data,
    train_val_split,
    normalize_apply,
    DATA_PATH,
    MODEL_PATH,
)
from nn_numpy import forward, compute_loss, predict


def confusion_counts(y_true, y_pred):
    y_true = y_true.astype(np.int32).reshape(-1)
    y_pred = y_pred.astype(np.int32).reshape(-1)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return tp, tn, fp, fn


def metrics_from_counts(tp, tn, fp, fn):
    eps = 1e-8
    acc = (tp + tn) / (tp + tn + fp + fn + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    return acc, precision, recall, f1


def load_saved_model(path):
    data = np.load(path, allow_pickle=True)
    params = {
        "W1": data["W1"],
        "b1": data["b1"],
        "W2": data["W2"],
        "b2": data["b2"],
        "W3": data["W3"],
        "b3": data["b3"],
    }
    mean = data["mean"]
    std = data["std"]
    feature_cols = data["feature_cols"].tolist()
    return params, mean, std, feature_cols


def main():
    if not MODEL_PATH.exists():
        print(f"Model file not found: {MODEL_PATH}")
        print("Run `python ml/train.py` first.")
        return

    X, y = load_data(DATA_PATH)
    X_tr, y_tr, X_val, y_val = train_val_split(X, y, val_ratio=0.2, seed=42)
    params, mean, std, feature_cols = load_saved_model(MODEL_PATH)
    if feature_cols:
        print(f"Loaded model with {len(feature_cols)} features from: {MODEL_PATH}")
    X_tr = normalize_apply(X_tr, mean, std)
    X_val = normalize_apply(X_val, mean, std)

    y_val_hat, _ = forward(X_val, params)
    val_loss = compute_loss(y_val_hat, y_val)

    y_pred = predict(X_val, params, threshold=0.5)
    tp, tn, fp, fn = confusion_counts(y_val, y_pred)
    acc, precision, recall, f1 = metrics_from_counts(tp, tn, fp, fn)

    print(f"val_loss:   {val_loss:.4f}")
    print(f"accuracy:   {acc:.4f}")
    print(f"precision:  {precision:.4f}")
    print(f"recall:     {recall:.4f}")
    print(f"f1:         {f1:.4f}")
    print("\nConfusion Matrix (actual x predicted)")
    print(f"TN={tn}  FP={fp}")
    print(f"FN={fn}  TP={tp}")


if __name__ == "__main__":
    main()