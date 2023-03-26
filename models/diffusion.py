# %%
import numpy as np
from scipy.integrate import solve_ivp
import colorama

colorama.init(autoreset=True)


def check_is_in_list(label, label_list):
    return label[0] in label_list


check_is_in_list = np.vectorize(check_is_in_list, excluded=(1,))


def colored(str, use_color=False):
    if use_color:
        return "{0}{1}{2}".format(
            colorama.Back.WHITE + colorama.Fore.BLACK, str, colorama.Style.RESET_ALL
        )
    else:
        return str


def print_matrix(matrix, color_condition=lambda xx: False):
    print_str = "\n".join(
        [
            " ".join(
                [
                    colored(("{0:.2f}".format(val)).rjust(6, " "), color_condition(val))
                    for val in line
                ]
            )
            for line in matrix
        ]
    )
    return print_str


def encode_id(elmt_id, encoding_map):
    return encoding_map[elmt_id]


encode_id = np.vectorize(encode_id, excluded=(1,))


class DiffusionSimulator2D:
    def __init__(self, pattern, variable_list, diffusion_coeffs, values):
        """Intialize function

        Args:
            pattern: An array containing characters symbolizing the areas of the medium.
            variable_list: List of labels specifying variable elements.
            diffusion_coeffs: A dictionary of diffusion coeffitients (e.g. {"V1":3})
            boundary_values: A dictionary of the boundary values
        """
        self._pattern = np.array(pattern)
        self._coeffs = diffusion_coeffs
        self._variable_list = variable_list
        self._variable_coordinate = np.argwhere(
            check_is_in_list(self._pattern, self._variable_list)
        )
        self._values = np.zeros_like(self._pattern, dtype=float)
        self.set_values(values)
        self.encode()

    def generate_backups(self):
        return {"pattern": self._pattern.copy(), "values": self._values.copy()}

    def restore_backups(self, backup):
        self._pattern = backup["pattern"].copy()
        self._values = backup["values"].copy()

    def set_product_diffusion(self, coeff):
        self._coeffs["P"] = coeff

    def encode(self):
        unique_var_id = np.unique(
            np.append(np.unique(self._pattern), np.unique(self._variable_list))
        )
        self._id_encoding = {
            code: ind for ind, code in enumerate(unique_var_id)
        }  # mapping str label -> int id
        self._pattern_encoded = encode_id(self._pattern, self._id_encoding)
        self._coeffs_encoded = [0.0] * len(self._id_encoding)
        for label, val in self._coeffs.items():
            self._coeffs_encoded[self._id_encoding[label]] = val

    def set_values(self, values):
        """Fill in the boundary values"""
        for key, val in values.items():
            self._values[self._pattern == key] = np.ravel(val)

    def extract_variables(self):
        return self._values[tuple(self._variable_coordinate.T)]

    def get_type_values(self, key):
        return self._values[self._pattern == key]

    def set_variables(self, y):
        self._values[tuple(self._variable_coordinate.T)] = y

    def equation(self, time, y, flag=False):
        matrix_data = self.get_value_copy(y)
        dy = np.zeros_like(y)
        for i, (xi, yi) in enumerate(self._variable_coordinate):
            dy[i] = (
                self._coeffs_encoded[self._pattern_encoded[xi, yi]]
                * (
                    (matrix_data[xi + 1, yi] + matrix_data[xi - 1, yi])
                    + (matrix_data[xi, yi + 1] + matrix_data[xi, yi - 1])
                    - 4 * matrix_data[xi, yi]
                )
                / 2
            )
        return dy

    def plot(self, plt, y=None):
        matrix_data = np.copy(self._values)
        if y is not None:
            matrix_data[tuple(self._variable_coordinate.T)] = y
        plt.imshow(
            matrix_data,
            cmap=plt.cm.viridis,
            alpha=0.9,
            interpolation="bilinear",
        )

    def get_value_copy(self, y):
        matrix_data = np.copy(self._values)
        matrix_data[tuple(self._variable_coordinate.T)] = y
        return matrix_data

    def integrate(self, delta_time, y0=None):
        if y0 is None:
            y0 = self.extract_variables()
        sol = solve_ivp(self.equation, [0, delta_time], y0)
        y_next = sol.y[:, -1]
        self.set_variables(y_next)
        # print("after, delta_time: {}".format(delta_time))
        # print(
        #     print_matrix(
        #         self.get_value_copy(sol.y[:, -1]), lambda val: np.isclose(val, 23)
        #     )
        # )
        # print()
        return y_next

    def display_values(self, y=None):
        if y is None:
            matrix_data = self._values
        else:
            matrix_data = self.get_value_copy(y)
        return print_matrix(matrix_data)

    def __str__(self):
        print_str = "\n".join(
            [
                " ".join([" " * (3 - len(character)) + character for character in line])
                for line in self._pattern
            ]
        )
        return print_str


# %%
if __name__ == "__main__":
    # Demo:
    import matplotlib.pyplot as plt

    pattern = (
        [["E"] * 9 + ["O"] * 20 + ["E"] * 4]
        + [["E"] + ["A"] * 31 + ["E"]] * 5
        + [["E"] + ["F"] * 31 + ["E"]]
        + [["E"] * 9 + ["O"] * 20 + ["E"] * 4]
    )
    diffusion_coefficients = {"A": 1, "E": 1, "O": 0.1, "F": 0.1}
    sim = DiffusionSimulator2D(
        pattern=pattern,
        variable_list=["A", "F"],
        diffusion_coeffs=diffusion_coefficients,
        values={"E": 23, "A": 23, "F": 150, "O": 150},
    )

    # %%

    times = np.linspace(0, 60, 50)
    t = times[0]
    y = [[24] * len(sim._variable_coordinate)]

    for t_next in times[1:]:
        y.append(sim.integrate(t_next - t, y[-1]))
        t = t_next
    y = np.array(y)
    plt.figure()
    plt.plot(times, y[:, 10])
    plt.xlabel("Time")
    plt.ylabel("Temp")
    plt.figure()
    plt.plot(times, y[:, -10])
    plt.xlabel("Time")
    plt.ylabel("Temp")
    plt.figure()
    res = sim.get_value_copy(y[-1])
    plt.plot(res[-2])
    plt.xlabel("X")
    plt.ylabel("Temp")


# %%
