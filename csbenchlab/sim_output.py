import bdsim.components as bd
from types import SimpleNamespace
class TimeseriesData:
    def __init__(self, time, data):
        self.Time = time
        self.Data = data

class SimOutput:
    def __init__(self, sim_output, watch_map: dict=None):
        if isinstance(sim_output, bd.BDStruct):
            self.parse_bdsim_output(sim_output, watch_map)


    def __getitem__(self, key):
        return getattr(self.parsed, key)

    def parse_bdsim_output(self, sim_output: bd, watch_map) -> dict:
        self.signals = SimpleNamespace()
        # parse all as timeseries data
        time_idx = watch_map.get("Time", None)
        if time_idx is not None:
            self.time = getattr(sim_output, f"y{time_idx}")
            time = self.time
        else:
            raise ValueError("Time signal not found in watch map.")
        watch_map.pop("Time", None)
        for watch_name, i in watch_map.items():
            if watch_name == "Reference":
                self.ref = \
                TimeseriesData(time, getattr(sim_output, f"y{i}"))
            else:
                splits = watch_name.split(".")
                if splits[0] == "Signals" and len(splits) >= 3:
                    block_name = splits[1]
                    signal_name = "_".join(splits[2:])
                    if not hasattr(self.signals, block_name):
                        setattr(self.signals, block_name, SimpleNamespace())
                    setattr(getattr(self.signals, block_name), signal_name,
                        TimeseriesData(time, getattr(sim_output, f"y{i}")))