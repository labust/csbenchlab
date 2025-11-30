import bdsim.components as bd


class SimOutput:
    def __init__(self, sim_output):
        self.parsed = {}
        if isinstance(sim_output, bd.BDStruct):
            self.parse_bdsim_output(sim_output)


    def __getitem__(self, key):
        return self.parsed[key]

    def parse_bdsim_output(self, sim_output: bd) -> dict:
        for i, var in enumerate(sim_output.ynames):
            var_name = f"y{i}"
            setattr(self, var, sim_output[var_name])
            self.parsed[var] = sim_output[var_name]