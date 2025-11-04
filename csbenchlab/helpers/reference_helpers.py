import numpy as np
from math import ceil
from csbenchlab.param_typing import *

def generate_steps(scenario, dt, system_dims, steps, dim):
    t_sim = scenario['SimulationTime']

    n_k = ceil(t_sim / dt)

    n_steps = len(steps)
    duration = ceil(n_k / n_steps)

    ref_x = np.zeros((n_steps * duration, system_dims["Outputs"]))

    n_k = len(ref_x)

    for i in range(n_steps):
        b = i * duration
        ref_x[b:b+duration, dim] = steps[i] * np.ones(duration)

    time = np.linspace(0, n_k-1, n_k) * dt

    return np.hstack((time.reshape(-1, 1), ref_x))