from csbenchlab.plugin import Controller
from csbenchlab.descriptor import ParamDescriptor
import numpy as np


class PID(Controller):

    param_description = [
        ParamDescriptor(name='Kp', default_value=1.0),
        ParamDescriptor(name='Ki', default_value=0.0),
        ParamDescriptor(name='Kd', default_value=0.0),
        ParamDescriptor(name='sat_min', default_value=-float('inf')),
        ParamDescriptor(name='sat_max', default_value=float('inf')),
    ]

    def on_configure(self):
        self._previous_error = 0.0
        self._integral = 0.0

    def wrap_angle(self, angle):
        """Wrap angle to [-pi, pi]."""
        return (angle + np.pi) % (2 * np.pi) - np.pi

    def on_step(self, y_ref, y, dt):
        error = y_ref - y
        u = self.params.Kp @ error

        if self.params.Ki != 0.0:
            self._integral += error * dt
            u += self.params.Ki * self._integral
        if self.params.Kd != 0.0:
            derivative = (error - self._previous_error) / dt if dt > 0 else 0.0
            u += self.params.Kd * derivative
            self._previous_error = error

        # Apply saturation limits
        u = np.maximum(self.params.sat_min, np.minimum(self.params.sat_max, u))

        # u = np.array([0])
        return u

