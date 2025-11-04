from pathlib import Path

from csbenchlab.data_desc import *

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


