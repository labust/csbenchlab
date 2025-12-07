from types import SimpleNamespace


class LogEntry(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"LogEntry(name={self.name})"

class DataModel(SimpleNamespace):
    pass


class ParamDescriptor(object):
    def __init__(self, name, default_value=0, type=None, description=""):
        self.name = name
        self.default_value = default_value
        self.type = type
        self.description = description

    # add subscriptable access
    def __getitem__(self, key):
        if key == 'Name':
            return self.name
        elif key == 'DefaultValue':
            return self.default_value
        elif key == 'Type':
            return self.type
        elif key == 'Description':
            return self.description
        else:
            raise KeyError(f"Key {key} not found in ParamDescription")

    def __repr__(self):
        return f"ParamDescriptor(name={self.name}, default_value={self.default_value}, type={self.type}, description={self.description})"


