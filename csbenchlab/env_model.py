from dataclasses import dataclass, field
from uuid import uuid4
from typing import List
from types import SimpleNamespace



def create_callbacks():
    return {
        "Initialize": "",
        "Step": "",
        "Reset": "",
        "Terminate": ""
    }

def new_uuid():
    return str(uuid4())

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
    ComponentType: str = "metadata"
    Metadata: dict = field(default_factory=lambda: {
        "Authors": [],
        "Version": "0.0.1",
        "License": "",
        "Tags": [],
        "Created": "",
        "Modified": ""
    })



@dataclass
class ComponentInfo:
    Id: str = field(default_factory=new_uuid)
    Name: str = ""
    Description: str = ""
    LibVersionHash: str = ""
    Lib: str = ""
    LibVersion: str = ""
    PluginType: str = ""
    PluginName: str = ""

@dataclass
class SubcomponentInfo:
    Id: str = field(default_factory=new_uuid)
    Name: str = ""
    Description: str = ""
    LibVersionHash: str = ""
    Lib: str = ""
    LibVersion: str = ""
    PluginType: str = ""
    PluginName: str = ""
    PluginImplementation: str = ""
    ParentComponentId: str = ""
    ParentComponentType: str = ""


@dataclass
@set_as_dict
class System(ComponentInfo):
    ComponentType: str = "system"
    Subcomponents: list = field(default_factory=lambda: ["Disturbance"])
    Disturbance: dict = field(default_factory=dict)


@dataclass
@set_as_dict
class Controller(ComponentInfo):
    IsComposable: bool = False
    RefHorizon: int = 0
    Mux: dict = field(default_factory=dict)
    ComponentType: str = "controller"
    Subcontrollers: List[dict] = field(default_factory=list)
    Subcomponents: list = field(default_factory=lambda: ["Subcontrollers"])
    Disturbance: dict = field(default_factory=dict)


@dataclass
@set_as_dict
class ControllerComponent(SubcomponentInfo):
    Mux: dict = field(default_factory=dict)
    ComponentType: str = "subcontroller"

@dataclass
@set_as_dict
class Scenario:
    Id: str = field(default_factory=new_uuid)
    Name: str = ""
    Description: str = ""
    ConstHorizonReference: bool = False
    ComponentType: str = "scenario"
    SimulationTime: float = 0.0
    Disturbance: dict = field(default_factory=dict)
    Subcomponents: list = field(default_factory=lambda: ["Disturbance"])

@dataclass
@set_as_dict
class Metric:
    Id: str = field(default_factory=new_uuid)
    Name: str = ""
    Description: str = ""
    ComponentType: str = "metric"

@dataclass
@set_as_dict
class Disturbance(SubcomponentInfo):
    ComponentType: str = "disturbance"

@dataclass
@set_as_dict
class Estimator(SubcomponentInfo):
    ComponentType: str = "estimator"


