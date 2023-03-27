import json
import os


def with_write_state(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.write_state()

    return wrapper


class HardStateManager:
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename) as f:
                self.states = json.load(f)
        else:
            self.states = {}

    @with_write_state
    def set_state(self, key, value):
        self.states[key] = value

    def get_state(self, key):
        return self.states.get(key)

    def write_state(self):
        with open(self.filename, "w") as f:
            json.dump(self.states, f)

    @with_write_state
    def clear_states(self):
        self.states = {}

    @with_write_state
    def delete_state(self, key):
        try:
            del self.states[key]
        except KeyError:
            pass
