
class LogEntry(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"LogEntry(name={self.name})"


class ParamDescriptor(object):
    def __init__(self, name, default_value):
        self.name = name
        self.default_value = default_value

    # add subscriptable access
    def __getitem__(self, key):
        if key == 'Name':
            return self.name
        elif key == 'DefaultValue':
            return self.default_value
        else:
            raise KeyError(f"Key {key} not found in ParamDescription")

    def __repr__(self):
        return f"ParamDescription(name={self.name}, default_value={self.default_value})"


