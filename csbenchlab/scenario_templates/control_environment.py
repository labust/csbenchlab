from typing import List
from csbenchlab.plugin import DynSystem, Controller
from csbenchlab.scenario_templates.csb_blocks import *
from csbenchlab.plugin_helpers import import_module_from_path
import bdsim as bd
from bdsim.blocks.sources import Constant, Time
from bdsim.blocks.sinks import Null
from bdsim.blocks.displays import Scope
import pickle

class ControlEnvironment:

    @staticmethod
    def components():
        return {
            "system": DynSystem,
            "controllers": List[ControllerBlock]
        }

    def __init__(self, env_name: str, backend=None):
        self.env_name = env_name
        self._module_classes = {}
        self._components = {}
        self.backend = backend

    def generate(self, comp_descriptions, blockdiagram, env_params, Ts, system_dims):
        d = blockdiagram
        self.import_component_modules(comp_descriptions)
        self.generate_component_instances(comp_descriptions, env_params, system_dims)
        clock = blockdiagram.clock(Ts, name="Clock")
        self.reference = Reference(name="Reference")
        self.const_Ts = Constant(Ts)
        self.time = Time(name="Time")
        d.add_block(self.reference)
        d.add_block(self.const_Ts)
        self.plants = []
        self.ctls = []
        self.scopes = []
        for i, controller in enumerate(self._components["controllers"]):
            scope = Scope(name="Scope" + f"_{i}", nin=2)
            d.add_block(scope)
            name = comp_descriptions["system"]["Name"] + f"_{i}"
            sys = comp_descriptions["system"]
            plant = PlantBlock(clock, sys, self._components["systems"][i], system_dims, name=name)
            d.add_block(plant)
            name = comp_descriptions["controllers"][i]["Name"]
            controller = ControllerBlock(clock, comp_descriptions["controllers"][i], self._components["controllers"][i], name=name)
            d.add_block(controller)
            null = Null(name="Null" + f"_{i}")
            d.add_block(null)
            d.connect(self.reference[0], controller[0])
            d.connect(plant[0], controller[1], scope[0])
            d.connect(self.const_Ts[0], controller[2])
            d.connect(controller[0], plant[0], scope[1])
            d.connect(self.time[0], plant[1])
            d.connect(self.const_Ts[0], plant[2])
            d.connect(controller[1], null[0])
            self.plants.append(plant)
            self.ctls.append(controller)
            self.scopes.append(scope)



    def set_scenario(self, scenario):
        self.reference.set_data(scenario["Reference"][:, 0], scenario["Reference"][:, 1:])
        for plant in self.plants:
            plant.obj.configure(scenario["SystemIc"])

        for i, controller in enumerate(self.ctls):
            controller.obj.configure()


    def generate_component_instances(self, comp_descriptions, env_params, system_dims):
        sys_params = env_params[comp_descriptions["system"]["Id"]]
        sys_cls = self._module_classes[comp_descriptions["system"]["Id"]]
        mux = {
            "Inputs": system_dims["Outputs"],
            "Outputs": system_dims["Inputs"],
        }
        self._components["controllers"] = []
        self._components["systems"] = []
        for ctrl_desc in comp_descriptions["controllers"]:
            sys = sys_cls('Params', sys_params)
            self._components["systems"].append(sys)
            cls = self._module_classes[ctrl_desc["Id"]]
            ctrl_params = env_params[ctrl_desc["Id"]]
            controller = cls('Params', ctrl_params, 'Mux', mux)
            self._components["controllers"].append(controller)


    def import_component_modules(self, comp_descriptions):
        for comp_type, comp_desc in comp_descriptions.items():
            if not isinstance(comp_desc, list):
                comp_desc = [comp_desc]
            for comp_desc in comp_desc:

                cls_name = comp_desc["PluginName"]
                info = self.backend.get_plugin_info_from_lib(comp_desc["PluginName"], comp_desc["Lib"])
                module_path = info["ComponentPath"]
                if module_path not in self._module_classes:
                    module = import_module_from_path(module_path)
                    if not hasattr(module, cls_name):
                        raise ValueError(f"Component class '{cls_name}' not found in module '{module_path}'.")
                    self._module_classes[comp_desc["Id"]] = getattr(module, cls_name)

