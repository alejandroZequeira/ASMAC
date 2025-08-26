import numpy as np
by_row = 1

class Problems:
    @staticmethod
    def dtlz1_g(Z, k):
        r = 100 * (k+(((Z - 0.5)**2) - np.cos(20*np.pi*(Z-0.5))).sum(axis=by_row))
        return r
    
    @staticmethod
    def dtlz1(X, m, M):
    
        r = None
    

        n = X.shape[1]
        j = M - 1
        k = n - j
    
        Y = X[:, :-k]
        Z = X[:, -k:]
    
        g = Problems.dtlz1_g(Z, k)
    

        if m == 0:
            r = (1.0 + g) * 0.5 * (Y.prod(axis=by_row))
    
    
        if m in range(1, M-1):
            r = (1.0 + g) * 0.5 * (Y[:, :M-m-1].prod(axis=by_row)) * (1 - Y[:, M-m-1])
    
    
        if m == M-1:
            r = (1.0 + g) * 0.5 * (1 - Y[:, 0])

        return r
    
    @staticmethod
    def evaluate_zdt1(x):
        f1 = x[0]
        g = 1 + 9 * sum(x[1:]) / (len(x) - 1)
        f2 = g * (1 - (f1 / g) ** 0.5)
        return [f1, f2]
    
    
    
    
