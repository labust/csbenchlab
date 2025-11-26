from csbenchlab.plugin import DynSystem
from csbenchlab.descriptor import ParamDescriptor
import numpy as np

class LinearSystem(DynSystem):


    param_description = [
        ParamDescriptor('A', np.zeros((1,1))),
        ParamDescriptor('B', np.zeros((1,1))),
        ParamDescriptor('C', np.zeros((1,1))),
        ParamDescriptor('D', np.zeros((1,1))),
        ParamDescriptor('sat_min', -np.inf),
        ParamDescriptor('sat_max', np.inf),
    ]

    @classmethod
    def get_dims_from_params(cls, params):
        return {
            "Inputs": params.B.shape[1],
            "Outputs": params.C.shape[0],
        }

    def on_configure(self):
        self.x_k = np.zeros((self.params.A.shape[0],))

    def on_step(self, u, t, dt, *args):
        # x_{k+1} = A*x_k + B*u
        self.x_k = self.params.A @ self.x_k + self.params.B @ u
        # y_k = C*x_k + D*u
        y_k = self.params.C @ self.x_k + self.params.D @ u
        # Apply saturation
        y_k = np.clip(y_k, self.params.sat_min, self.params.sat_max)
        return y_k

    def on_reset(self):
        self.x_k = np.zeros((self.A.shape[0],))