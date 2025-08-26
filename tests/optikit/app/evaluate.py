import numpy as np
from optikit.problems.problem import Problems

def evaluate_population(population):
    return np.array([Problems.dtlz1(ind) for ind in population])
