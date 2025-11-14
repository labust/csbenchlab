import casadi as ca

class CasadiDict:

    def __init__(self, value_dict):
        self._idx = {}
        self._values = []
        i = 0
        for key, value in value_dict.items():
            self._idx[key] = i
            if isinstance(value, (int, float)):
                v = ca.MX.sym(key)
            elif isinstance(value, (list, tuple)):
                v = ca.MX.sym(key, len(value))
            elif isinstance(value, ca.MX) or isinstance(value, ca.SX):
                v = value
            else:
                v = ca.MX.sym(key, value.shape)
            self._values.append(v)
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
        else:
            raise AttributeError(f"'CasadiDict' object has no attribute '{key}'")

    @property
    def values(self):
        return [x for x in self._values if (isinstance(x, ca.MX) or isinstance(x, ca.SX))]
