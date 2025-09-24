from dataclasses import dataclass, field
from uuid import uuid4



def create_callbacks():
    return {
        "Initialize": "",
        "Step": "",
        "Reset": "",
        "Terminate": ""
    }

def set_as_dict(cls):
    def as_dict():
        r = {}
        fields = cls.__dataclass_fields__
        for field_ in fields:
            if hasattr(cls, field_):
                v = getattr(cls, field_)
                if isinstance(v, list):
                    r[field_] = [item if not hasattr(item, 'as_dict') else item.as_dict() for item in v]
                elif hasattr(v, 'as_dict'):
                    r[field_] = v.as_dict()
                else:
                    r[field_] = v
            else:
                if fields[field_].default_factory is not None:
                    r[field_] = fields[field_].default_factory()
                elif fields[field_].default is not None:
                    r[field_] = fields[field_].default
                else:
                    r[field_] = None
        return r

    cls.as_dict = as_dict
    return cls

@dataclass
@set_as_dict
class Metadata:
    Name: str = "New Environment"
    Description: str = ""
    Author: str = ""
    Version: str = "0.0.1"
    License: str = ""
    Tags: list = field(default_factory=list)
    Created: str = ""
    Modified: str = ""



@dataclass
class ComponentInfo:
    Id: str = str(uuid4())
    Name: str = ""
    Description: str = ""
    ParamsFile: str = ""
    LibraryVersionHash: str = ""
    Library: str = ""
    LibraryVersion: str = ""
    PluginType: str = ""
    Callbacks: dict = field(default_factory=create_callbacks)


@dataclass
@set_as_dict
class System(ComponentInfo):
    Disturbance: dict = field(default_factory=dict)
    Estimator: dict = field(default_factory=dict)
    Callbacks: dict = field(default_factory=create_callbacks)


@dataclass
@set_as_dict
class Controller(ComponentInfo):
    IsComposable: bool = False
    RefHorizon: int = 0
    Mux: dict = field(default_factory=dict)
    Components: list = field(default_factory=list)
    Disturbance: dict = field(default_factory=dict)
    Estimator: dict = field(default_factory=dict)


@dataclass
@set_as_dict
class ControllerComponent:
    Id: str = str(uuid4())
    Name: str = ""
    Description: str = ""
    ParamsFile: str = ""
    LibraryVersionHash: str = ""
    Library: str = ""
    LibraryVersion: str = ""
    PluginType: str = ""
    Callbacks: dict = field(default_factory=create_callbacks)
    Mux: dict = field(default_factory=dict)

@dataclass
@set_as_dict
class Scenario:
    Id: str = str(uuid4())
    Name: str = ""
    Description: str = ""
    InitialCondition: str = ""
    Reference: str = ""
    ParamsFile: str = ""
    ConstHorizonReference: bool = False

@dataclass
@set_as_dict
class Metric:
    Id: str = str(uuid4())
    Name: str = ""
    Description: str = ""
    ParamsFile: str = ""
    Callback: str = ""


@dataclass
@set_as_dict
class Disturbance(ComponentInfo):
    pass

@dataclass
@set_as_dict
class Estimator(ComponentInfo):
    pass

