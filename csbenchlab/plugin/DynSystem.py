from abc import abstractmethod
from . import PluginBase
import numpy as np


class DynSystem(PluginBase):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._is_configured = False
        parsed = self.parse_positional_args(args)
        self.params = parsed.get('Params', {})
        self.is_simulink = parsed.get('is_simulink', False)
        self.data = parsed.get('Data', None)
        self.last_el = None
        if hasattr(self, 'create_data_model') and self.data is None:
            self.data = self.create_data_model(self.params)
        self.initialize(**kwargs)

    @classmethod
    @abstractmethod
    def get_dims_from_params(cls, params):
        raise NotImplementedError()

    @classmethod
    def create_data_model(cls, params):
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

    def configure(self, ic=None, **kwargs):
        self._is_configured = True
        dims = self.get_dims_from_params(self.params)
        if ic is not None:
            assert len(ic) == dims["Outputs"], "Initial conditions length does not match number of outputs."
            self._ic = ic
        else:
            self._ic = np.zeros(dims["Outputs"])
        self.last_el = self._ic
        return self.on_configure()

    def step(self, u, t, dt, *args, **kwargs):
        result = self.on_step(u, t, dt, *args)
        self.last_el = result
        return result

    def reset(self):
        return self.on_reset()