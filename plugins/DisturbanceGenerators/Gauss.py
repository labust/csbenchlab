from csbenchlab.plugin import DisturbanceGenerator
from csbenchlab.descriptor import ParamDescriptor
import numpy as np

class Gauss(DisturbanceGenerator):

    param_description = [
        ParamDescriptor(name='mean', default_value=0.0),
        ParamDescriptor(name='stddev', default_value=1.0),
    ]

    def on_step(self, y, dt):

        noise = np.random.normal(self.params.mean, self.params.stddev, size=np.shape(y))
        return y + noise