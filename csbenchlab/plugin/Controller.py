from abc import abstractmethod

import json
from . import PluginBase
import numpy as np

class Controller(PluginBase):


    def __init__(self, *args, **kwargs):
        super().__init__()
        self._is_configured = False
        parsed = self.parse_positional_args(args)
        self.params = parsed.get('Params', {})
        self.is_simulink = parsed.get('is_simulink', False)
        self.data = parsed.get('Data', None)
        mux = parsed.get('Mux', None)
        self.mux = mux
        self.last_el = None
        if hasattr(self, 'create_data_model') and self.data is None:
            self.data = self.create_data_model(self.params, mux)
        self.initialize(**kwargs)


    @classmethod
    def create_data_model(cls, params, mux):
        """Create and return a data model for the controller."""
        return None

    def on_configure(self):
        """Called when the controller is configured with parameters."""
        pass

    def on_step(self):
        """Called on each step with the current parameters."""
        pass

    def on_reset(self):
        """Called to reset the controller state."""
        pass

    def configure(self, ic=None, *args, **kwargs):
        if ic is not None:
            if self.mux is not None:
                assert len(ic) == self.mux["Outputs"], "Initial conditions length does not match number of outputs."
            self._ic = ic
        else:
            if self.mux is not None:
                self._ic = np.zeros(self.mux["Outputs"])
            else:
                self._ic = np.zeros(1)
        self.last_el = self._ic
        self._is_configured = True
        return self.on_configure()

    def step(self, y_ref, y, dt, *args, **kwargs):
        result = self.on_step(np.array(y_ref), np.array(y), np.double(dt), *args)
        self.last_el = result
        return result

    def reset(self):
        return self.on_reset()