from abc import abstractmethod

from . import DynSystem
import numpy as np
from csbenchlab.casadi_dict import CasadiDict
from csbenchlab.descriptor import DataModel
import casadi as ca


class CasadiDynSystem(DynSystem):

    casadi_plugin__ = True
    is_pure__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data is not None:
            self.data_as_casadi = CasadiDict(self.data.__dict__)
        else:
            self.data_as_casadi = CasadiDict({})

        # Overload casadi functions
        self.casadi_configure()
        self.step_fns = self.casadi_step_fn_()

    @abstractmethod
    def casadi_step_fn(self):
        pass

    def on_configure(self):
        self.data_as_casadi.x = ca.DM(self._ic)

    def casadi_configure(self):
        pass

    def casadi_step_fn_(self):
        return self.casadi_step_fn()

    def update_data(self, new_data):
        for key, value in new_data.items():
            key_without_new = key.replace('new_', '')
            if hasattr(self.data, key) \
                or hasattr(self.data, key_without_new):
                setattr(self.data, key_without_new, value)
        return self.data

    def on_step(self, u, t, dt, data=None, *args, **kwargs):
        if data is None:
            data = self.data_as_casadi
        d = {
            'u': u,
            't': t,
            'dt': dt,
            **data.__dict__
        }
        for i, fn in enumerate(self.step_fns):
            inputs = self.prepare_inputs(fn, d)
            sol = fn(**inputs)
            d = self.update_inputs(fn, sol, d)
        # TODO add integrator
        if 'dx' in sol:
            data.x += sol["dx"] * dt
        else:
            data.x = sol['x']
        res = np.array(sol['dx'])
        self.last_el = res[:, 0]
        return self.last_el

    @classmethod
    def create_data_model(cls, params):
        dims = cls.get_dims_from_params(params)
        return DataModel(
           x=ca.DM.zeros(dims["Outputs"])
        )

    def update_inputs(self, fn, out, d):
        for i, name in enumerate(fn.name_out()):
            d[name] = out[name]
        return d

    def prepare_inputs(self, fn, d):
        inputs = {}
        for name in fn.name_in():
            if name in d:
                inputs[name] = d[name]
        return inputs

    def on_reset(self):
        pass



class CasadiDiscreteDynSystem(DynSystem):
    pass


class CasadiContinuousDynSystem(CasadiDynSystem):
    """Continuous-time dynamical system with CasADi integration."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.integrator = self._build_integrator(num_steps=1)


    def _build_integrator(self, integrator_type='rk', num_steps=1):
        """Build a CasADi integrator (RK4 or Cvodes) with dt as a parameter."""
        dae_fn = self.step_fns
        if isinstance(dae_fn, list) and len(dae_fn) == 1:
            dae_fn = dae_fn[0]

        if not isinstance(dae_fn, ca.Function):
            raise ValueError('casadi_dae_fn() must return a CasADi Function.')

        # Extract state and control dimensions from function
        n_in = dae_fn.n_in()
        if n_in < 2:
            raise ValueError('casadi_dae_fn must have at least 2 inputs: x and u.')

        x_sym = ca.MX.sym('x', dae_fn.size1_in(0))
        u_sym = ca.MX.sym('u', dae_fn.size1_in(1))

        dx = dae_fn(x_sym, u_sym)
        dae = {'x': x_sym, 'p': u_sym, 'ode': dx}
        if integrator_type == 'rk':
            integrator = ca.integrator('rk4_integrator', 'rk', dae,
                                       {"number_of_finite_elements": num_steps, "tf": 0.01})
        else:
            integrator = ca.integrator('integrator', integrator_type, dae,
                                       {"number_of_finite_elements": num_steps, "tf": 0.01})
        return integrator

    def on_step(self, u, t, dt, data=None, *args, **kwargs):
        """Integrate dynamics from current state over time dt with input u."""
        if data is None:
            data = self.data_as_casadi

        x0 = data.x
        u = ca.DM(u).reshape((-1, 1))

        integrated = self.integrator(x0=x0, p=u)
        x_next = ca.DM(integrated['xf'])
        data.x = x_next
        self.last_el = np.array(x_next).ravel()
        return self.last_el