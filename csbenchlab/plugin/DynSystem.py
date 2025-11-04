from abc import abstractmethod
from . import PluginBase


class DynSystem(PluginBase):


    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def on_configure(self, params):
        """Called when the controller is configured with parameters."""
        pass

    @abstractmethod
    def on_step(self, params):
        """Called on each step with the current parameters."""
        pass

    @abstractmethod
    def on_reset(self):
        """Called to reset the controller state."""
        pass