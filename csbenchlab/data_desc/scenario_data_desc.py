from pathlib import Path
from csbenchlab.data_desc import DataDescBase, get_default_callbacks_txt_file

class ScenarioDataDesc(DataDescBase):


    def __init__(self, component_path):
        super().__init__(component_path)

    @property
    def files(self):
        return {
            'scenario.py': lambda x: self.get_default_scenario_txt_file(x),
            'callbacks.py': lambda x: get_default_callbacks_txt_file(x),
            # 'ic.py': lambda x: self.get_default_ic_txt_file(x),
            # 'reference.py': lambda x:  self.get_default_ref_txt_file(x),
        }

    def get_default_override_system_params_txt_file(self, scenario):
        return f"""from csbenchlab.common_types import *

# Override system parameters file for scenario {scenario.get('Id', '')}

# Implement this to override certain system parameters for the scenario
def override_system_params(system_params):
    return system_params
"""

    def get_default_ic_txt_file(self, scenario):
        return f"""from csbenchlab.helpers.ic_helpers import *
import numpy as np

# Initial conditions file for scenario {scenario.get('Id', '')}

# Implement this to generate initial conditions for the scenario
def ic(scenario, system_dims):
    return np.zeros(system_dims["Outputs"])
"""

    def get_default_ref_txt_file(self, scenario):
        return f"""from csbenchlab.helpers.reference_helpers import *
import numpy as np

# Reference file for scenario {scenario.get('Id', '')}

# Implement this to generate reference values for the scenario
def reference(scenario, dt, system_dims):
    pass
"""


    def get_default_scenario_txt_file(self, scenario):
        return """from csbenchlab.helpers.reference_helpers import *
from csbenchlab.helpers.ic_helpers import *
from csbenchlab.common_types import*
import numpy as np

def scenario(scenario, dt, system_dims):

    overrides = {}
    reference = generate_steps(scenario, dt, system_dims, [1], 0)
    ic = np.zeros((system_dims["Outputs"]))

    return ScenarioOptions(
        reference=reference,
        ic=ic,
        system_parameter_overrides=overrides
    )
"""