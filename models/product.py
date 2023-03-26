# %%
from models.diffusion import DiffusionSimulator2D
from models.quality_functions import q_energy_smooth
import numpy as np


class Product:
    def __init__(
        self,
        product_id,
        pattern,
        position,
        init_temperature,
        energy,
        diffusion_coefficient,
    ) -> None:
        self._id = product_id
        self._pattern = np.array(pattern)
        self.shape = self._pattern.shape
        self._position = np.array(position)
        self._values = np.tile(init_temperature, self._pattern.shape)
        self._energy = energy
        self._diffusion_coefficient = diffusion_coefficient
        self._history = {}

    def __str__(self):
        print_str = "\n".join(
            [
                " ".join([" " * (3 - len(character)) + character for character in line])
                for line in self._pattern
            ]
        )
        return print_str

    def record_simulator(self, environment, state):
        if self._history == {}:
            energy_values = np.zeros_like(self._pattern, dtype=float)
        else:
            self.read_temperature(environment)
            energy_values = np.copy(self._values) / state["speed"]
        self._history[state["time"]] = {
            "energy_values": energy_values,
            "temperature_values": np.copy(self._values),
        }
        self._history[state["time"]].update(state)

    def update_position(self, new_pos):
        self._position = new_pos

    def get_position(self):
        return self._position

    def set_environment(self, environment):
        x_0, y_0 = self._position
        x_1, y_1 = self._position + self._pattern.shape
        environment._pattern[x_0:x_1, y_0:y_1] = self._pattern
        environment._values[x_0:x_1, y_0:y_1] = self._values
        return environment

    def read_temperature(self, environment):
        x_0, y_0 = self._position
        x_1, y_1 = self._position + self._values.shape
        self._values = environment._values[x_0:x_1, y_0:y_1]

    def get_values(self):
        return self._values

    def get_pattern(self):
        return self._pattern

    def is_end_traidmill(self, environment):
        return self._position[1] + self.shape[1] >= environment._values.shape[1] - 1

    def product_statistics(self):
        cumulated_energy = np.sum(
            [dat["energy_values"] for dat in self._history.values()], axis=0
        )
        speeds = [dat["speed"] for dat in self._history.values()]
        temperatures = [dat["temperature"] for dat in self._history.values()]
        temperatures_ext = [dat["temperature_ext"] for dat in self._history.values()]
        times = np.sort([time for time in self._history.keys()])
        return {
            "product_id": self._id,
            "quality": np.mean(q_energy_smooth(cumulated_energy, self._energy)),
            "time_spent": times[-1] - times[0],
            "speed": np.mean(speeds),
            "temperature": np.mean(temperatures),
            "temperature_ext": np.mean(temperatures_ext),
        }


# %%)
