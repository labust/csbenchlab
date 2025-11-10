from pathlib import Path

from csbenchlab.data_desc import *

def get_component_context_path(component):
    if "ParentComponentType" not in component:
        return Path(COMPONENT_DATA_DESC[component["ComponentType"]]["destination_path"]) / component["Id"]
    parent_type = component.get("ParentComponentType", None)
    if parent_type not in COMPONENT_DATA_DESC:
        raise ValueError(f"Unknown parent component type: {parent_type}")
    parent_id = component.get("ParentComponentId", None)
    if parent_id is None or parent_id == "":
        raise ValueError(f"Subcomponent must have 'ParentComponentId' field")
    comp_type = component["ComponentType"]
    subctl_path = Path(COMPONENT_DATA_DESC[parent_type]["destination_path"]) / parent_id / 'subcomponents'
    subctl_path = subctl_path / COMPONENT_DATA_DESC[comp_type]["destination_path"] / component["Id"]
    return subctl_path

def get_component_relative_param_file_path(component):
    return Path('params') / f"{component['Id']}.py"

def get_component_param_file_path(component):
    return get_component_context_path(component) \
        / get_component_relative_param_file_path(component)

COMPONENT_DATA_DESC = {
    'controller': {
        "destination_path": Path('parts') / 'controllers',
        "data_file": 'controller.json',
        "params_path": 'params',
        "data_desc_class": ControllerDataDesc,
        "standalone": True
    },
    'system': {
        "destination_path": Path('parts') / 'systems',
        "data_file": 'system.json',
        "params_path": 'params',
        "data_desc_class": SystemDataDesc,
        "standalone": True
    },
    'scenario': {
        "destination_path": Path('parts') / 'scenarios',
        "data_file": 'scenario.json',
        "data_desc_class": ScenarioDataDesc,
        "standalone": True
    },
    'metric': {
        "destination_path": Path('parts') / 'metrics',
        "data_file": 'metric.json',
        "data_desc_class": MetricDataDesc,
        "standalone": True
    },
    'metadata': {
        "destination_path": 'config.json',
        "data_file": '',
        "standalone": True
    },
    'disturbance': {
        'destination_path': 'disturbances',
        "data_file": 'disturbance.json',
        "params_path": 'params',
        "standalone": False
    },
    'estimator': {
        "destination_path": 'estimators',
        "data_file": 'estimator.json',
        "params_path": 'params',
        "standalone": False
    },
    'subcontroller': {
        "destination_path": 'subcontrollers',
        "data_file": 'subcontroller.json',
        "params_path": 'params',
        "standalone": False
    }
}


