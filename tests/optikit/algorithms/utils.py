import math




def euclidean_dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

def init_weights(n_subproblems):
    weights = []
    for i in range(n_subproblems):
        w = i / (n_subproblems - 1)
        weights.append([w, 1 - w])
    return weights

def get_neighbors(weights, T):
    neighbors = []
    for i, w in enumerate(weights):
        dists = [(j, euclidean_dist(w, weights[j])) for j in range(len(weights))]
        dists.sort(key=lambda x: x[1])
        neighbors.append([j for j, _ in dists[:T]])
    return neighbors

def scalarizing_chebyshev(f, weight, z):
    return max(weight[i] * abs(f[i] - z[i]) for i in range(len(f)))
