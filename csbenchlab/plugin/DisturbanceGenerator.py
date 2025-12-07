from abc import abstractmethod
from . import PluginBase
import numpy as np


class DisturbanceGenerator(PluginBase):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._is_configured = False
        parsed = self.parse_positional_args(args)
        self.params = parsed.get('Params', {})
        self.system_dims = parsed.get('SystemDims', {})
        self.is_simulink = parsed.get('is_simulink', False)
        self.data = parsed.get('Data', None)
        self.last_el = None
        if hasattr(self, 'create_data_model') and self.data is None:
            self.data = self.create_data_model(self.params)
        self.initialize(**kwargs)

    def on_configure(self):
        """Called when the controller is configured with parameters."""
        pass

    @abstractmethod
    def on_step(self, y, dt):
        """Called on each step with the current parameters."""
        pass

    def on_reset(self):
        """Called to reset the controller state."""
        pass

    def configure(self, ic=None, **kwargs):
        self._is_configured = True
        if ic is not None:
            if self.system_dims:
                assert len(ic) == self.system_dims["Outputs"], "Initial conditions length does not match number of outputs."
            self._ic = ic
        else:
            if self.system_dims:
                self._ic = np.zeros(self.system_dims["Outputs"])
            else:
                raise ValueError("System dimensions must be provided to set initial conditions.")
        self.last_el = self._ic
        return self.on_configure()

    def step(self, u, dt, *args, **kwargs):
        result = self.on_step(u, dt, *args)
        self.last_el = result
        return result

    def reset(self):
        return self.on_reset()