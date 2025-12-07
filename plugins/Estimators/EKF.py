from csbenchlab.plugin import Estimator
from csbenchlab.descriptor import ParamDescriptor
import numpy as np


class EKF(Estimator):

    param_description = [
        ParamDescriptor(name='Q', default_value=None),
        ParamDescriptor(name='R', default_value=None),
        ParamDescriptor(name='x0', default_value=None),
        ParamDescriptor(name='P0', default_value=None),
        ParamDescriptor(name='eps', default_value=1e-6),
    ]

    def on_configure(self):
        # Measurement function `h` must be provided by the user (attribute or via initialize)
        if not hasattr(self, 'h') or self.h is None:
            raise ValueError('EKF requires a measurement function `h(x)`. Set `est.h = callable` before configure.')

        # Initialize state estimate
        x0 = getattr(self, 'x0', None)
        if x0 is None:
            # try infer size from P0
            P0 = getattr(self, 'P0', None)
            if P0 is not None:
                n = np.atleast_2d(P0).shape[0]
                self.x = np.zeros(n)
            else:
                self.x = np.zeros(1)
        else:
            self.x = np.ravel(np.array(x0, dtype=float))

        # Initialize covariance
        P0 = getattr(self, 'P0', None)
        if P0 is None:
            self.P = np.eye(self.x.size) * 1.0
        else:
            self.P = np.atleast_2d(np.array(P0, dtype=float))

        # Q and R
        Q = getattr(self, 'Q', None)
        if Q is None:
            self.Q = np.eye(self.x.size) * 1e-6
        else:
            Q = np.array(Q, dtype=float)
            if Q.ndim == 0:
                self.Q = np.eye(self.x.size) * float(Q)
            else:
                self.Q = np.atleast_2d(Q)

        R = getattr(self, 'R', None)
        if R is None:
            # attempt to infer measurement dimension
            try:
                y0 = np.ravel(np.array(self.h(self.x)))
                m = y0.size
            except Exception:
                m = 1
            self.R = np.eye(m) * 1e-3
        else:
            R = np.array(R, dtype=float)
            if R.ndim == 0:
                try:
                    y0 = np.ravel(np.array(self.h(self.x)))
                    m = y0.size
                except Exception:
                    m = 1
                self.R = np.eye(m) * float(R)
            else:
                self.R = np.atleast_2d(R)

        # Optional functions
        self.f = getattr(self, 'f', None)
        self.F_jac = getattr(self, 'F_jac', None)
        self.H_jac = getattr(self, 'H_jac', None)

        self._eps = float(getattr(self, 'eps', 1e-6))

    def numeric_jacobian(self, func, x, dt=None):
        x = np.ravel(np.array(x, dtype=float))
        n = x.size
        # base evaluation
        try:
            if dt is None:
                y0 = np.ravel(np.array(func(x)))
            else:
                y0 = np.ravel(np.array(func(x, dt)))
        except Exception:
            x_col = x.reshape((-1, 1))
            if dt is None:
                y0 = np.ravel(np.array(func(x_col)))
            else:
                y0 = np.ravel(np.array(func(x_col, dt)))
        m = y0.size
        J = np.zeros((m, n))
        for i in range(n):
            dx = np.zeros(n)
            dx[i] = self._eps
            xp = x + dx
            try:
                if dt is None:
                    yp = np.ravel(np.array(func(xp)))
                else:
                    yp = np.ravel(np.array(func(xp, dt)))
            except Exception:
                xp_col = xp.reshape((-1, 1))
                if dt is None:
                    yp = np.ravel(np.array(func(xp_col)))
                else:
                    yp = np.ravel(np.array(func(xp_col, dt)))
            J[:, i] = (yp - y0) / self._eps
        return J

    def on_step(self, y, dt):
        """Predict and update step.

        Parameters
        - y: measurement (array-like)
        - dt: time step forwarded to `f` if it accepts dt
        """
        y = np.ravel(np.array(y, dtype=float))

        # Predict
        if self.f is None:
            x_pred = self.x.copy()
            F = np.eye(self.x.size)
        else:
            try:
                x_pred = np.ravel(np.array(self.f(self.x, dt)))
            except TypeError:
                x_pred = np.ravel(np.array(self.f(self.x)))

            if self.F_jac is not None:
                try:
                    F = np.atleast_2d(np.array(self.F_jac(self.x, dt), dtype=float))
                except TypeError:
                    F = np.atleast_2d(np.array(self.F_jac(self.x), dtype=float))
            else:
                F = self.numeric_jacobian(self.f, self.x, dt)

        # Covariance predict
        self.P = F @ self.P @ F.T + self.Q

        # Update
        try:
            y_pred = np.ravel(np.array(self.h(x_pred)))
        except Exception:
            y_pred = np.ravel(np.array(self.h(x_pred.reshape((-1, 1)))))

        if self.H_jac is not None:
            H = np.atleast_2d(np.array(self.H_jac(x_pred), dtype=float))
        else:
            H = self.numeric_jacobian(self.h, x_pred)

        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)

        innovation = (y - y_pred)
        if innovation.ndim == 0:
            innovation = innovation.reshape((1,))
        self.x = x_pred + (K @ innovation).ravel()

        I = np.eye(self.P.shape[0])
        self.P = (I - K @ H) @ self.P

        return self.x

    def on_reset(self):
        x0 = getattr(self, 'x0', None)
        if x0 is not None:
            self.x = np.ravel(np.array(x0, dtype=float))
        P0 = getattr(self, 'P0', None)
        if P0 is not None:
            self.P = np.atleast_2d(np.array(P0, dtype=float))