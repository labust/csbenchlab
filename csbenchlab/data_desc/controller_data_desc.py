from csbenchlab.data_desc import DataDescBase, get_default_callbacks_txt_file

class ControllerDataDesc(DataDescBase):


    def __init__(self, component_path):
        super().__init__(component_path)

    @property
    def files(self):
        return {
            'callbacks.py': lambda x: get_default_callbacks_txt_file(x),
        }
