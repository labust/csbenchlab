import numpy as np
from math import ceil
from csbenchlab.common_types import *


def generate_sin_reference(scenario, dt, system_dims, amplitudes, frequencies, dim):
    t_sim = scenario['SimulationTime']

    n_k = ceil(t_sim / dt)

    ref_x = np.zeros((n_k, system_dims["Outputs"]))

    time = np.linspace(0, n_k-1, n_k) * dt
    sin_time = np.floor(len(time) / len(amplitudes)) # time for one sinusoid period
    # make phi such that sinusoids are continuous at the borders of their periods

    for i in range(len(amplitudes)):
        st_time = i * sin_time * dt
        end_time = (i+1) * sin_time * dt
        mask = (time >= st_time) & (time < end_time)
        ref_x[mask, dim] = amplitudes[i] * np.sin(2 * np.pi * frequencies[i] * time[mask])
        # phi for next segment ensures continuity at boundary

    return np.hstack((time.reshape(-1, 1), ref_x))



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


def constant(value, scenario_or_tsim, dt):
    if isinstance(scenario_or_tsim, dict):
        scenario = scenario_or_tsim
        t_sim = scenario['SimulationTime']
    else:
        t_sim = scenario_or_tsim
    n_k = ceil(t_sim / dt)

    time = np.linspace(0, n_k-1, n_k) * dt
    ref_x = np.tile(value.reshape(1, -1), (n_k, 1))

    return np.hstack((time.reshape(-1, 1), ref_x))
