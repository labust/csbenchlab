
from csbenchlab.plugin import CasadiDynSystem
import casadi as ca

class MovingCartInvertedPendulum(CasadiDynSystem):

    """ Moving Cart with Inverted Pendulum System
    The system consists of a cart that can move horizontally and an inverted pendulum
    attached to the cart. The goal is to control the cart's movement to keep the
    pendulum balanced in the upright position.

    States:
        x: horizontal position of the cart (m)
        x_dot: horizontal velocity of the cart (m/s)
        theta: angle of the pendulum from vertical (0 is upright) (rad)
        theta_dot: angular velocity of the pendulum (rad/s)
    """


    @classmethod
    def get_dims_from_params(cls, params):
        return {
            "Inputs": 2,
            "Outputs": 4
        }

    def casadi_configure(self):
        # Physical constants with sensible defaults (SI units)
        # M: cart mass (kg), m: pendulum mass (kg), l: pendulum length to COM (m)
        # b: cart friction coefficient (N s / m), g: gravity (m/s^2)
        self.M = float(getattr(self.params, 'M', 1.0))
        self.m = float(getattr(self.params, 'm', 0.1))
        self.l = float(getattr(self.params, 'l', 0.5))
        self.b = float(getattr(self.params, 'b', 0.1))
        self.g = float(getattr(self.params, 'g', 9.81))

        # state and derivative placeholders (4 states: x, x_dot, theta, theta_dot)
        self.x = ca.MX(4, 1)
        self.dx = ca.MX(4, 1)

    def casadi_step_fn(self):
        # inputs: u[0] = horizontal force on cart (N)
        #         u[1] = torque applied at pendulum pivot (N m) (optional disturbance)
        u = ca.MX(2, 1)

        # states: x, x_dot, theta, theta_dot
        x = self.x[0]
        x_dot = self.x[1]
        theta = self.x[2]
        theta_dot = self.x[3]

        M = self.M
        m = self.m
        l = self.l
        b = self.b
        g = self.g

        F = u[0]
        tau = u[1]

        s = ca.sin(theta)
        c = ca.cos(theta)

        # Intermediate terms
        denom = M + m*(1 - c**2)

        # theta double dot (including pivot torque tau)
        theta_ddot = (g*s - (c*(F + m*l*theta_dot**2*s - b*x_dot) + tau/(m*l)) / denom) / (l*(4.0/3.0 - (m*c**2)/denom))

        # x double dot
        x_ddot = (F + m*l*(theta_dot**2*s - theta_ddot*c) - b*x_dot) / (M + m)

        # assemble derivative vector
        self.dx[0] = x_ddot
        self.dx[1] = theta_ddot
        self.dx[2] = x_dot
        self.dx[3] = theta_dot

        return [ca.Function('moving_cart_inverted_pendulum', [self.x, u], [self.dx], ["x", "u"], ["dx"])]

