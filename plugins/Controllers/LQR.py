from csbenchlab.plugin import CasadiController
from csbenchlab.descriptor import ParamDescriptor
import casadi as ca
import numpy as np

try:
    from scipy import linalg as _spla
except Exception:
    _spla = None


class LQR(CasadiController):


    param_description = [
        ParamDescriptor(name='K', default_value=None),
        ParamDescriptor(name='synthesize', default_value=False),
        ParamDescriptor(name='A', default_value=None),
        ParamDescriptor(name='B', default_value=None),
        ParamDescriptor(name='Q', default_value=None),
        ParamDescriptor(name='R', default_value=None),
        ParamDescriptor(name='discrete', default_value=False),
        ParamDescriptor(name='sat_min', default_value=-np.inf),
        ParamDescriptor(name='sat_max', default_value=np.inf),
    ]

    def casadi_configure(self):
        # Prepare the gain K. If synthesis requested, compute LQR gain using SciPy.
        self._K_py = None
        if bool(getattr(self.params, 'synthesize', False)):
            if _spla is None:
                raise RuntimeError('SciPy is required for synthesis but is not available.')
            A = getattr(self.params, 'A', None)
            B = getattr(self.params, 'B', None)
            if A is None or B is None:
                raise ValueError('To synthesize LQR controller, provide `A` and `B` in params.')
            A = np.atleast_2d(np.array(A, dtype=float))
            B = np.atleast_2d(np.array(B, dtype=float))

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

            if bool(getattr(self.params, 'discrete', False)):
                # discrete-time LQR: solve discrete ARE
                P = _spla.solve_discrete_are(A, B, Q, R)
                # K = (B' P B + R)^{-1} B' P A
                K = np.linalg.inv(B.T @ P @ B + R) @ (B.T @ P @ A)
            else:
                # continuous-time LQR
                P = _spla.solve_continuous_are(A, B, Q, R)
                # K = R^{-1} B' P
                K = np.linalg.inv(R) @ (B.T @ P)

            # store K such that control law is u = -K (x - x_ref)
            self._K_py = K
        else:
            self._K_py = getattr(self.params, 'K', None)

        return None

    def casadi_step_fn(self):
        # define inputs
        y_ref = ca.MX.sym('y_ref', self.mux["Inputs"])
        y = ca.MX.sym('y', self.mux["Inputs"])
        dt = ca.MX.sym('dt')

        # Determine K to use
        K_py = self._K_py
        if K_py is None:
            # fallback to zero gain
            K_py = 0.0

        # Convert to CasADi DM
        if np.isscalar(K_py):
            if self.mux["Inputs"] == self.mux["Outputs"]:
                K = ca.DM(np.eye(self.mux["Outputs"]) * float(K_py))
            else:
                K = ca.DM(np.ones((self.mux["Outputs"], self.mux["Inputs"])) * float(K_py))
        else:
            K_arr = np.array(K_py)
            K = ca.DM(K_arr)

        # tracking error (state error)
        e = (y - y_ref)

        # LQR control law: u = -K * e
        u_unclamped = -ca.mtimes(K, e)

        # apply saturation
        sat_min = float(self.params.sat_min)
        sat_max = float(self.params.sat_max)
        u = ca.fmin(ca.fmax(u_unclamped, sat_min), sat_max)

        fn = ca.Function('lqr_controller', [y_ref, y, dt], [u], ["y_ref", "y", "dt"], ["u"])
        return [fn]

