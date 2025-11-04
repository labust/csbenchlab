from .descriptor import ParamDescription

class SetParams(object):
    def __init__(self, *args):
        self.params = args
        for i, arg in enumerate(args):
            if isinstance(arg, ParamDescription):
                setattr(self, arg.name, arg.default_value)
            elif isinstance(arg, dict):
                for key, value in arg.items():
                    setattr(self, key, value)
            else:
                raise TypeError(f"Invalid type for ParamSet argument {i}: {type(arg)}")

    def __iter__(self):
        return iter(self.params)

    def __len__(self):
        return len(self.params)
