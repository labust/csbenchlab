from abc import ABC


class PluginBase(ABC):

    param_description = []
    log_description = []
    input_description = []
    output_description = []


    def initialize(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def parse_positional_args(self, args):
        """Parse positional arguments and return a dictionary of parameters."""
        if len(args) == 0:
            return {}
        i = 0
        parsed = {}
        while True:
            if i >= len(args):
                break
            if isinstance(args[i], str):
                if i + 1 < len(args):
                    parsed[args[i]] = args[i + 1]
                else:
                    parsed[args[i]] = None
            i += 2
        return parsed