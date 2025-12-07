from csbenchlab.plugin import CasadiController
from csbenchlab.descriptor import ParamDescriptor
import casadi as ca
import numpy as np
from scipy import linalg as spla


class HInfinity(CasadiController):

    param_description = [
        ParamDescriptor(name='K', default_value=1.0),
        ParamDescriptor(name='sat_min', default_value=-np.inf),
        ParamDescriptor(name='sat_max', default_value=np.inf),
        ParamDescriptor(name='synthesize', default_value=False),
        ParamDescriptor(name='A', default_value=None),
        ParamDescriptor(name='B', default_value=None),
        ParamDescriptor(name='Q', default_value=None),
        ParamDescriptor(name='R', default_value=None),
    ]

    def casadi_configure(self):
        # If synthesis is requested, attempt to compute a state-feedback gain K
        # via continuous-time LQR as an approximation to an H-infinity design.
        # NOTE: This assumes the measured signal `y` corresponds to the full state x
        # (i.e. C = I). If that's not the case, provide `K` manually.
        self._K_py = None
        if bool(getattr(self.params, 'synthesize', False)):
            A = getattr(self.params, 'A', None)
            B = getattr(self.params, 'B', None)
            if A is None or B is None:
                raise ValueError('To synthesize a controller, provide `A` and `B` in params.')
            A = np.atleast_2d(np.array(A, dtype=float))
            B = np.atleast_2d(np.array(B, dtype=float))

            # Default weightings if not provided: Q = C^T C approx I, R = I
            Q = getattr(self.params, 'Q', None)
            R = getattr(self.params, 'R', None)
            if Q is None:
                Q = np.eye(A.shape[0])
            else:
                Q = np.atleast_2d(np.array(Q, dtype=float))
            if R is None:
                R = np.eye(B.shape[1])
            else:
                R = np.atleast_2d(np.array(R, dtype=float))

            # Solve continuous-time algebraic Riccati equation for LQR
            P = spla.solve_continuous_are(A, B, Q, R)
            # LQR gain (u = -K x)
            K = np.linalg.inv(R) @ (B.T @ P)
            self._K_py = -K
        else:
            # use provided K as-is
            self._K_py = getattr(self.params, 'K', 1.0)
        return None

    def casadi_step_fn(self):
        # define inputs
        y_ref = ca.MX.sym('y_ref', self.mux["Inputs"])
        y = ca.MX.sym('y', self.mux["Inputs"])
        dt = ca.MX.sym('dt')

        # Build gain matrix K from previously computed `_K_py` or provided parameter.
        K_py = self._K_py if hasattr(self, '_K_py') else getattr(self.params, 'K', 1.0)

        # Convert to CasADi DM or MX constant
        if np.isscalar(K_py):
            # If scalar and square mapping, build diagonal; otherwise scalar times ones matrix
            if self.mux["Inputs"] == self.mux["Outputs"]:
                K = ca.DM(np.eye(self.mux["Outputs"]) * float(K_py))
            else:
                K = ca.DM(np.ones((self.mux["Outputs"], self.mux["Inputs"])) * float(K_py))
        else:
            # Try to convert array-like to DM
            K_arr = np.array(K_py)
            K = ca.DM(K_arr)

        # error signal
        e = (y_ref - y)

        # control law: u = K * e
        u_unclamped = -ca.mtimes(K, e)

        # apply elementwise saturation using provided params
        sat_min = float(self.params.sat_min)
        sat_max = float(self.params.sat_max)

        # create saturation as casadi expressions (works for scalar or vector u)
        u = ca.fmin(ca.fmax(u_unclamped, sat_min), sat_max)

        # Return a single CasADi function producing the control `u`.
        fn = ca.Function('h_infinity_controller', [y_ref, y, dt], [u], ["y_ref", "y", "dt"], ["u"])
        return [fn]

