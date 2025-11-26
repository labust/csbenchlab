from abc import abstractmethod

import json
from typing import overload
from . import PluginBase, Controller
import numpy as np
import casadi as ca
from csbenchlab.casadi_dict import CasadiDict


class CasadiController(Controller):

    casadi_plugin__ = True
    is_pure__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data is not None:
            self.data_as_casadi = CasadiDict(self.data.__dict__)
        else:
            self.data_as_casadi = CasadiDict({})

        # Overload casadi functions
        self.casadi_configure()
        self.step_fns = self.casadi_step_fn_()

    @abstractmethod
    def casadi_step_fn(self):
        pass

    def on_configure(self):
        pass

    def casadi_configure(self):
        pass

    def casadi_step_fn_(self):
        return self.casadi_step_fn()

    @classmethod
    def create_data_model(cls, params, mux):
        """Create and return a data model for the controller."""
        return None


    def update_data(self, new_data):
        for key, value in new_data.items():
            key_without_new = key.replace('new_', '')
            if hasattr(self.data, key) \
                or hasattr(self.data, key_without_new):
                setattr(self.data, key_without_new, value)
        return self.data

    def on_step(self, y_ref, y, dt, data=None, *args, **kwargs):
        if data is None:
            data = self.data_as_casadi
        d = {
            'y_ref': y_ref,
            'y': y,
            'dt': dt,
            **data.__dict__
        }
        for i, fn in enumerate(self.step_fns):
            inputs = self.prepare_inputs(fn, d)
            sol = fn(**inputs)
            d = self.update_inputs(fn, sol, d)
        res = np.array(sol['out'])
        self.last_el = res[:, 0]
        return self.last_el


    def update_inputs(self, fn, out, d):
        for i, name in enumerate(fn.name_out()):
            d[name] = out[name]
        return d

    def prepare_inputs(self, fn, d):
        inputs = {}
        for name in fn.name_in():
            if name in d:
                inputs[name] = d[name]
        return inputs

    def on_reset(self):
        raise Exception("Casadi components do not implement reset function.")
