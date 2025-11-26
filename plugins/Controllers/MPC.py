from csbenchlab.plugin import CasadiController
from csbenchlab.descriptor import ParamDescriptor
import casadi as ca


class MPC(CasadiController):

    param_description = [
        ParamDescriptor(name='L', default_value=1),
        ParamDescriptor(name='A', default_value=0.0),
        ParamDescriptor(name='B', default_value=0.0),
        ParamDescriptor(name='C', default_value=0.0),
        ParamDescriptor(name='D', default_value=0.0),
        ParamDescriptor(name='sat_min', default_value=-float('inf')),
        ParamDescriptor(name='sat_max', default_value=float('inf')),
        ParamDescriptor(name="Q", default_value=1.0),
        ParamDescriptor(name="R", default_value=1.0),

    ]

    def casadi_configure(self):
        # define the casadi MPC solver here

        self.x0 = ca.SX.sym('x0', self.params.A.shape[0], 1)  # state
        self.y_ref = ca.SX.sym('x_ref', self.params.A.shape[0], 1)  # reference state
        L = int(self.params.L)
        cost = 0
        X = self.x0
        U = []
        g = []
        for k in range(L):
            u_k = ca.SX.sym(f'u_{k}', self.params.B.shape[1], 1)
            X = self.params.A @ X + self.params.B @ u_k
            Y = self.params.C @ X + self.params.D @ u_k
            cost += ca.sumsqr(Y - self.y_ref) @ self.params.Q + ca.sumsqr(u_k) @ self.params.R
            g.append(u_k - self.params.sat_max < 0)
            g.append(self.params.sat_min - u_k < 0)
            U.append(u_k)


        opts = {'ipopt.print_level': 0, 'print_time': 0}
        nlp = {'x': ca.vertcat(*U), 'f': cost, 'g': ca.vertcat(*g), 'p': ca.vertcat(self.x0, self.y_ref)}
        self.solver = ca.nlpsol('solver', 'ipopt', nlp, opts)

    def casadi_step_fn(self):
        prepare_data = ca.vertcat(self.x0, self.y_ref)
        prepare_data = ca.Function('prepare_data', [self.x0, self.y_ref], [prepare_data], ['y', 'y_ref'], ['p'])
        # dimension of x vector in solver
        x = ca.MX.sym('x', self.params.B.shape[1] * self.params.L)
        u = x[0:self.params.B.shape[1]]


        out = ca.Function('mpc_step', [x], [u], ["x"], ['out'])
        return [prepare_data, self.solver, out]

