from typing import Any
from types import SimpleNamespace

class DataModel(SimpleNamespace):
    pass

class ScenarioOptions():

    def __init__(self,
                 reference,
                 ic=[],
                 system_parameter_overrides={},
                 disturbance_parameter_overrides={},
                 num_evaluations=1,
                 random_seed=42
                 ):
        self.data = {
            "SystemIc": ic,
            "SystemParameterOverrides": system_parameter_overrides,
            "Reference": reference,
            "DisturbanceParameterOverrides": disturbance_parameter_overrides,
            "NumEvaluations": num_evaluations,
            "RandomSeed": random_seed
        }

class PyFunctionHandle(str):
    pass

class MatFunctionHandle(str):
    pass


class MultiScenario:

    def __init__(self, params, num_samples: int, generator: Any = None, random_seed: int = None):
        self.params = params
        self.num_samples = num_samples
        self.generator = generator
        self.random_seed = random_seed

class PyEval:

    def __init__(self, eval_str: str):
        self.eval_str = eval_str

    def eval(self):
        return eval(self.eval_str)


class MatEval:

    def __init__(self, eval_str: str):
        self.eval_str = eval_str

    def as_string(self):
        return f"csb_m_eval_exp:{self.eval_str}"

class MatFileEval:

    def __init__(self, eval_str: str):
        self.file_path = eval_str

    def as_string(self):
        return f"csb_m_eval_file:{self.file_path}"


class LoadFromFile:

    def __init__(self, file_path: str, var_name: str = None):
        self.file_path = file_path
        self.var_name = var_name

    @classmethod
    def cls_as_string(cls):
        try:
            path = cls.file_path
            var = cls.var_name
            return f"csb_load_from_file:{path}:{var}" if var else f"csb_load_from_file:{path}"
        except AttributeError:
            raise ValueError("Class does not have 'file_path' or 'var_name' attributes")

    def as_string(self):
        return f"csb_load_from_file:{self.file_path}:{self.var_name}" \
            if self.var_name else f"csb_load_from_file:{self.file_path}"



# load from file decorator for class
def load_from_file(file_path: str, var_name: str = None):
    def decorator(cls):
        cls.load_from_file__ = True
        cls.file_path = file_path
        cls.var_name = var_name
        cls.as_string = lambda: f"csb_load_from_file:{cls.file_path}:{cls.var_name}" \
            if cls.var_name else f"csb_load_from_file:{cls.file_path}"
        return cls
    return decorator


# MATLAB function decorator
def matlab_function(function_name: str, **kwargs):
    def decorator(func):
        func.external_function__ = function_name
        func.external_backend__ = 'm'
        func.external_kwargs__ = kwargs
        return func
    return decorator
