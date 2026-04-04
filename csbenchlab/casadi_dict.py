import casadi as ca
import numpy as np

class CasadiDict:

    def __init__(self, value_dict):
        self._idx = {}
        self._values = []
        i = 0
        for key, value in value_dict.items():
            self._idx[key] = i
            if isinstance(value, (int, float)):
                v = ca.DM(value)
            elif isinstance(value, (list, tuple, np.ndarray)):
                v = ca.DM(value)
            elif isinstance(value, ca.DM):
                v = value
            elif isinstance(value, ca.MX) or isinstance(value, ca.SX):
                raise ValueError("CasadiDict does not support MX or SX types as input values.")
            else:
                raise ValueError(f"Unsupported type for CasadiDict value: {type(value)}")
            self._values.append(v)
            setattr(self, key, v)
            i += 1

    def __getattr__(self, item):
        if item == '_idx' or item == '_values':
            return super().__getattribute__(item)
        if item == 'keys':
            return self._idx.keys()
        if item in self._idx:
            return self._values[self._idx[item]]
        else:
            raise AttributeError(f"'CasadiDict' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key in ['_idx', '_values']:
            super().__setattr__(key, value)
        elif key in self._idx:
            self._values[self._idx[key]] = value
            super().__setattr__(key, value)
        else:
            raise AttributeError(f"'CasadiDict' object has no attribute '{key}'")

    @property
    def values(self):
        return [x for x in self._values]
