from csbenchlab.plugin import CasadiController
from csbenchlab.descriptor import ParamDescriptor
import casadi as ca
import numpy as np


class SlidingMode(CasadiController):
    """Sliding Mode Controller with chattering reduction via saturation.

    The sliding surface is defined as: s = C * e
    where e = y_ref - y is the tracking error.

    Control law: u = -K * sign(s) - F * s
    with sign smoothed by saturation: u = -K * sat(s/epsilon) - F * s
    """

    param_description = [
        ParamDescriptor(name='C', default_value=1.0),
        ParamDescriptor(name='K', default_value=1.0),
        ParamDescriptor(name='F', default_value=0.1),
        ParamDescriptor(name='epsilon', default_value=0.1),
        ParamDescriptor(name='sat_min', default_value=-np.inf),
        ParamDescriptor(name='sat_max', default_value=np.inf),
    ]

    def casadi_configure(self):
        # Parameters are accessed in casadi_step_fn
        pass

    def casadi_step_fn(self):
        # define inputs
        y_ref = ca.MX.sym('y_ref', self.mux["Inputs"])
        y = ca.MX.sym('y', self.mux["Inputs"])
        dt = ca.MX.sym('dt')

        # Build sliding surface matrix C
        C = getattr(self.params, 'C', 1.0)
        if np.isscalar(C):
            if self.mux["Inputs"] == self.mux["Outputs"]:
                C_mat = ca.DM(np.eye(self.mux["Outputs"]) * float(C))
            else:
                C_mat = ca.DM(np.ones((self.mux["Outputs"], self.mux["Inputs"])) * float(C))
        else:
            C_mat = ca.DM(np.array(C, dtype=float))

        # Gain parameters
        K = self.params.K
        F = self.params.F
        epsilon = self.params.epsilon

        # Saturation bounds
        sat_min = self.params.sat_min
        sat_max = self.params.sat_max

        # Tracking error
        e = y_ref - y

        # Sliding surface: s = C * e
        s = ca.mtimes(C_mat, e)

        # Smoothed sign function using saturation to reduce chattering
        # sign(s) ≈ sat(s/epsilon, -1, 1)
        sign_s_smooth = ca.fmin(ca.fmax(s / epsilon, -1.0), 1.0)

        # Sliding mode control law with discontinuous and continuous terms
        # u = -K * sign(s) - F * s
        u_sm = -K * sign_s_smooth - F * s

        # Apply saturation limits
        u = ca.fmin(ca.fmax(u_sm, sat_min), sat_max)

        return [ca.Function('sliding_mode_controller', [y_ref, y, dt], [u], ["y_ref", "y", "dt"], ["u"])]

