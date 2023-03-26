#%%
from math import sqrt
import numpy as np


def q_energy_old(E):
    return 100 - 2 * abs(173 - (1.73 * E))


def q_energy_smooth(E, E0=100):
    gap = (E0 - E) ** 2
    return 100 - 2 * (0.5 * gap if gap < 1 else sqrt(gap) - 0.5)


q_energy_smooth = np.vectorize(q_energy_smooth)
