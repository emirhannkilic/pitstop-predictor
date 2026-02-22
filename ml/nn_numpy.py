import numpy as np

def init_params(n_x=9, n_h1=16, n_h2=8, seed=42):
    rng = np.random.default_rng(seed)

    W1 = rng.standard_normal((n_x, n_h1)) * np.sqrt(2.0 / n_x)
    b1 = np.zeros((1, n_h1))

    W2 = rng.standard_normal((n_h1, n_h2)) * np.sqrt(2.0 / n_h1)
    b2 = np.zeros((1, n_h2))

    # output layer
    W3 = rng.standard_normal((n_h2, 1)) * np.sqrt(2.0 / n_h2)
    b3 = np.zeros((1, 1))

    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2, "W3": W3, "b3": b3}


def relu(x):
    return np.maximum(0.0, x)


def relu_grad(x):
    return (x > 0).astype(np.float64)


def sigmoid(x):
    x = np.clip(x, -50, 50)  # limit overflow
    return 1.0 / (1.0 + np.exp(-x))


def forward(X, params):
    W1, b1 = params["W1"], params["b1"]
    W2, b2 = params["W2"], params["b2"]
    W3, b3 = params["W3"], params["b3"]

    Z1 = np.dot(X, W1) + b1 
    A1 = relu(Z1)

    Z2 = np.dot(A1, W2) + b2
    A2 = relu(Z2)

    Z3 = np.dot(A2, W3) + b3
    y_hat = sigmoid(Z3)

    cache = {"X": X, "Z1": Z1, "A1": A1, "Z2": Z2, "A2": A2, "Z3": Z3, "y_hat": y_hat}
    return y_hat, cache


def compute_loss(y_hat, y):
    eps = 1e-8
    y_hat = np.clip(y_hat, eps, 1.0 - eps)  # limit overflow
    loss = -np.mean(y * np.log(y_hat) + (1.0 - y) * np.log(1.0 - y_hat))
    return loss


def backward(params, cache, y):

    X = cache["X"]      # (m, 9)
    Z1 = cache["Z1"]    # (m, 16)
    A1 = cache["A1"]    # (m, 16)
    Z2 = cache["Z2"]    # (m, 8)
    A2 = cache["A2"]    # (m, 8)
    y_hat = cache["y_hat"]  # (m, 1)

    W2 = params["W2"]   # (16, 8)
    W3 = params["W3"]   # (8, 1)

    m = X.shape[0]


    dZ3 = y_hat - y                     # (m, 1)
    dW3 = np.dot(A2.T, dZ3) / m         # (8, 1)
    db3 = np.sum(dZ3, axis=0, keepdims=True) / m  # (1, 1)

    dA2 = np.dot(dZ3, W3.T)             # (m, 8)
    dZ2 = dA2 * relu_grad(Z2)           # (m, 8)
    dW2 = np.dot(A1.T, dZ2) / m         # (16, 8)
    db2 = np.sum(dZ2, axis=0, keepdims=True) / m  # (1, 8)

    dA1 = np.dot(dZ2, W2.T)             # (m, 16)
    dZ1 = dA1 * relu_grad(Z1)           # (m, 16)
    dW1 = np.dot(X.T, dZ1) / m          # (9, 16)
    db1 = np.sum(dZ1, axis=0, keepdims=True) / m  # (1, 16)

    grads = {
        "dW1": dW1, "db1": db1,
        "dW2": dW2, "db2": db2,
        "dW3": dW3, "db3": db3,
    }
    return grads


def update_params(params, grads, lr=0.01):
    params["W1"] -= lr * grads["dW1"]
    params["b1"] -= lr * grads["db1"]
    params["W2"] -= lr * grads["dW2"]
    params["b2"] -= lr * grads["db2"]
    params["W3"] -= lr * grads["dW3"]
    params["b3"] -= lr * grads["db3"]
    return params


def predict_proba(X, params):
    y_hat, _ = forward(X, params)
    return y_hat


def predict(X, params, threshold=0.5):
    proba = predict_proba(X, params)
    return (proba >= threshold).astype(np.int32)