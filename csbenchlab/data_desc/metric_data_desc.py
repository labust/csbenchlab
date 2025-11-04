from csbenchlab.data_desc import DataDescBase, get_default_callbacks_txt_file

class MetricDataDesc(DataDescBase):


    def __init__(self, component_path):
        super().__init__(component_path)

    @property
    def files(self):
        return {
            'metric.py': lambda x: self.default_txt_file(x),
            'callbacks.py': lambda x: get_default_callbacks_txt_file(x),
        }

    def default_txt_file(self, metric):
        return f"""from csbenchlab.helpers.metric_helpers import *
import numpy as np

# Reference file for metric {metric.get('Id', '')}

# Implement this to generate reference values for the metric
def metric(results):
    pass
"""
