import random
from math import exp


def sample_temperature(time_step, temperature, target, attractor_intensity):
    delta_center = (target - temperature) * attractor_intensity
    return temperature + random.gauss(delta_center, time_step)


def evolve_inertia(time_step, current_value, setting, tau):
    return setting + (current_value - setting) * exp(-time_step / tau)
