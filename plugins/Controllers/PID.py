from csbenchlab.plugin import Controller
from csbenchlab.descriptor import ParamDescriptor


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

    def on_step(self, y_ref, y, dt):
        error = y_ref - y
        self._integral += error * dt
        derivative = (error - self._previous_error) / dt if dt > 0 else 0.0

        u = (self.params.Kp * error +
             self.params.Ki * self._integral +
             self.params.Kd * derivative)

        # Apply saturation limits
        u = max(self.params.sat_min, min(self.params.sat_max, u))

        self._previous_error = error
        return u

