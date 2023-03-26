import simulation_api
from models.product import Product
import numpy as np
import random
from loguru import logger
from models.evolution_functions import evolve_inertia
from models.quality_functions import q_energy_smooth
from models.diffusion import DiffusionSimulator2D
from models.diffusion import print_matrix

ARENA_PATTERN = (
    [["E"] * 9 + ["O"] * 20 + ["E"] * 4]
    + [["E"] + ["A"] * 31 + ["E"]] * 5
    + [["E"] + ["F"] * 31 + ["E"]]
    + [["E"] * 9 + ["O"] * 20 + ["E"] * 4]
)
ARENA_PATTERN = (
    [["E"] * 4 + ["O"] * 10 + ["E"] * 4]
    + [["E"] + ["A"] * 16 + ["E"]] * 5
    + [["E"] + ["F"] * 16 + ["E"]]
    + [["E"] * 4 + ["O"] * 10 + ["E"] * 4]
)
PRODUCT_PATTERN = [["P"] * 3] * 3


def get_joint_parameters(mu1, sigma1, mu2, sigma2):
    mu_join = (sigma2**2 * mu1 + sigma1**2 * mu2) / (sigma1**2 + sigma2**2)
    sigma_join = np.sqrt((sigma1**2 * sigma2**2) / (sigma1**2 + sigma2**2))
    return mu_join, sigma_join


class OvenAPI(simulation_api.API_Model):
    def setup(self):
        self._product_id_counter = 0
        self._product_list = []
        self._diffusion_simulator = DiffusionSimulator2D(
            pattern=np.array(ARENA_PATTERN),
            variable_list=["P", "F", "A"],
            diffusion_coeffs=self._param["diffusion_coeff"],
            values={
                "E": self._param["temp_ext_init"],
                "O": self._param["temp_init"],
                "A": self._param["temp_ext_init"],
                "F": self._param["temp_ext_init"],
            },
        )
        self._backups = {}

    def generate_backups(self, state):
        self._backups["state"] = {key: val for key, val in state.items()}
        self._backups[
            "diffusion_simulator"
        ] = self._diffusion_simulator.generate_backups()

    def restore_backups(self):
        self._diffusion_simulator.restore_backups(self._backups["diffusion_simulator"])
        return {key: val for key, val in self._backups["state"].items()}

    def sample_temperature(self, current_T, time_step):
        ext_param = self._param["temperature_ext"]
        mu_join, sigma_join = get_joint_parameters(
            ext_param["mean"],
            ext_param["scale"],
            current_T,
            ext_param["step_scale"] * time_step,
        )
        return np.random.normal(mu_join, sigma_join)

    def check_add_product(self, init_temperature):
        """Add a new product only if the beginning of the treadmill is free."""
        energy = np.random.uniform(
            self._param["products_variability"]["energy_min"],
            self._param["products_variability"]["energy_max"],
        )
        diffusion_coeff = np.random.uniform(
            self._param["products_variability"]["coeff_min"],
            self._param["products_variability"]["coeff_max"],
        )
        self._diffusion_simulator.set_product_diffusion(diffusion_coeff)
        if len(self._product_list) == 0 or np.all(
            self._diffusion_simulator._pattern[
                5,
                1 : self._product_list[-1].shape[1]
                + 1
                + self._param["product_spacing"],
            ]
            == "A"
        ):
            self._product_list.append(
                Product(
                    self.get_new_product_id(),
                    PRODUCT_PATTERN,
                    [3, 1],
                    init_temperature,
                    energy,
                    diffusion_coeff,
                )
            )

    def check_remove_product(self, state):
        if self._product_list[0].is_end_traidmill(self._diffusion_simulator):
            removed_product = self._product_list.pop(0)
            return removed_product
        return None

    def get_new_product_id(self):
        returned_id = self._product_id_counter
        self._product_id_counter += 1
        return returned_id

    def clear_diffusion_simulator(self):
        """Remove all the product informations from the simulator."""
        self._diffusion_simulator._pattern[
            self._diffusion_simulator._pattern == "P"
        ] = "A"

    def update_product_positions(self, shift):
        self.clear_diffusion_simulator()
        for product in self._product_list:
            product.read_temperature(self._diffusion_simulator)
            product.update_position(product.get_position() + np.array([0, shift]))
            self._diffusion_simulator = product.set_environment(
                self._diffusion_simulator
            )

    def apply_setting_intertia(self, state, time_step):
        state["temperature"] = evolve_inertia(
            time_step,
            state["temperature"],
            state["temperature_setting"],
            self._param["temperature_inertia"],
        )
        state["speed"] = evolve_inertia(
            time_step,
            state["speed"],
            state["speed_setting"],
            self._param["speed_inertia"],
        )
        state["temperature_ext"] = self.sample_temperature(
            state["temperature_ext"], time_step
        )
        return state

    def record_simulator(self, state):
        for product in self._product_list:
            product.record_simulator(self._diffusion_simulator, state)

    def compute_outputs(self, param):
        state = {key: val for key, val in param.items()}
        if self._backups == {}:  # First call
            self.generate_backups(state)
        else:
            state = self.restore_backups()
        state.update(
            {key: val for key, val in param.items() if key in self._settings.keys()}
        )
        self.check_add_product(self._param["temperature_ext"])
        state["optimal_energy"] = self._product_list[0]._energy
        state["product_diffusion_coeff"] = self._product_list[0]._diffusion_coefficient
        removed_product = None
        while removed_product is None:
            time_step = 1 / state["speed"]
            state["time"] += time_step
            state = self.apply_setting_intertia(state, time_step / 2)
            self.update_simulator_settings(state)
            self._diffusion_simulator.integrate(time_step)
            state = self.apply_setting_intertia(state, time_step / 2)
            self.update_simulator_settings(state)
            self.record_simulator(state)
            self.update_product_positions(shift=1)
            removed_product = self.check_remove_product(state)

        state.update(removed_product.product_statistics())
        state["is_set"] = True
        return state

    def compute_next_state(self):
        state, _ = self.get_state()
        self._backups = {}
        if state == {}:
            return self.generate_initial_state()
        state["is_set"] = False
        state["id"] += 1
        state = self.compute_outputs(state)
        return state

    def generate_initial_state(self):
        temp_ext = self.sample_temperature(self._param["temperature_ext"]["mean"], 5)
        speed_init = self._param["speed_init"]
        temp_init = self._param["temp_init"]
        state = {
            "id": 0,
            "speed": speed_init,
            "speed_setting": speed_init,
            "temperature": temp_init,
            "temperature_setting": temp_init,
            "temperature_ext": temp_ext,
            "product_id": 0,
            "optimal_energy": 0,
            "product_diffusion_coeff": 0,
            "time_spent": 0,
            "quality": 0,
            "time": 0,
            "is_set": False,
        }
        self.record_simulator(state)
        return state

    def update_simulator_settings(self, state):
        self._diffusion_simulator.set_values(
            {"O": state["temperature"], "E": state["temperature_ext"]}
        )
