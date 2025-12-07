from typing import List
from csbenchlab.plugin import DynSystem, Controller
from csbenchlab.scenario_templates.csb_blocks import *
from csbenchlab.plugin_helpers import import_module_from_path, get_plugin_class_from_info
from csbenchlab.eval_parameters import eval_plugin_params
import bdsim as bd
from bdsim.blocks.sources import Constant, Time
from bdsim.blocks.sinks import Null
from bdsim.blocks.displays import Scope
from m_scripts.eval_scenario_descriptions import eval_scenario_descriptions
from csbenchlab.sim_output import SimOutput



class ControlEnvironment:

    @staticmethod
    def components():
        return {
            "system": DynSystem,
            "controllers": List[ControllerBlock]
        }

    def __init__(self, env_path: str, env_metadata:dict, backend=None):
        self.env_path = env_path
        self.env_name = env_metadata.get("Name", "GeneratedEnvironment")
        self.data = env_metadata
        self.Ts = env_metadata.get("Ts", 0.01)
        self._module_classes = {}
        self._components = {}
        self.backend = backend
        self.sim = BDSim()
        self.scenarios = []
        self._watchers = []
        self._watch_map = {}

        self.d = self.sim.blockdiagram(name=self.env_name)

    def watch_time(self, time):
        watch_name = f"Time"
        self._watch_map[watch_name] = len(self._watchers)
        self._watchers.append(time)

    def watch_reference(self, reference):
        watch_name = f"Reference"
        self._watch_map[watch_name] = len(self._watchers)
        self._watchers.append(reference)

    def watch_signal(self, signal_name: str, signal, override_name_from_block=None):
        if override_name_from_block is not None:
            block_name = override_name_from_block.block.name
        else:
            block_name = signal.block.name
        watch_name = f"Signals.{block_name}.{signal_name}"
        self._watch_map[watch_name] = len(self._watchers)
        self._watchers.append(signal)

    def generate(self, comp_descriptions, env_params, generate_scopes=False, live_metrics=None):
        d = self.d
        Ts = self.Ts
        self.import_component_modules(comp_descriptions)

        sys = comp_descriptions["system"]
        system_dims = self.backend.get_system_dims(sys, env_params[sys["Id"]])
        self.generate_component_instances(comp_descriptions, env_params, system_dims)
        clock = d.clock(Ts, name="Clock")
        self.reference = Reference(name="Reference")
        self.const_Ts = Constant(Ts)
        self.time = Time(name="Time")
        d.add_block(self.reference)
        d.add_block(self.const_Ts)
        self.plants = []
        self.ctls = []
        self.scopes = []
        self.live_metrics = live_metrics if live_metrics is not None else []
        self.watch_time(self.time[0])
        self.watch_reference(self.reference[0])
        self.plant_noise_blocks = []
        for i, controller in enumerate(self._components["controllers"]):
            ctl_name = comp_descriptions["controllers"][i]["Name"]
            controller = ControllerBlock(clock, comp_descriptions["controllers"][i], self._components["controllers"][i], name=ctl_name)
            d.add_block(controller)
            sys_name = comp_descriptions["system"]["Name"] + f"_{i}"
            plant = PlantBlock(clock, sys, self._components["systems"][i], system_dims, name=sys_name)
            d.add_block(plant)
            null = Null(name="Null" + f"_{i}")
            d.add_block(null)
            plant_noise = NoiseBlock(clock, system_dims)
            d.add_block(plant_noise)
            d.connect(plant[0], plant_noise[0])
            d.connect(self.reference[0], controller[0])
            d.connect(self.const_Ts[0], controller[2])
            d.connect(self.time[0], plant[1])
            d.connect(self.const_Ts[0], plant[2])
            d.connect(self.const_Ts[0], plant_noise[1])
            d.connect(controller[1], null[0])
            d.connect(plant_noise[0], controller[1])
            d.connect(controller[0], plant[0])
            self.plant_noise_blocks.append(plant_noise)
            self.plants.append(plant)
            self.ctls.append(controller)
            self.watch_signal("u", controller[0])
            self.watch_signal("y", plant[0], controller[0])
            self.watch_signal("y_n", plant_noise[0], controller[0])
            if i == 0:
                system_metric = SystemMetric(self.live_metrics)
                d.add_block(system_metric)
                d.connect(plant_noise[0], system_metric[0])
            if generate_scopes:
                scope = Scope(name="Scope" + f"_{i}", nin=2, )
                d.add_block(scope)
                d.connect(plant_noise[0], scope[0])
                d.connect(controller[0], scope[1])
                self.scopes.append(scope)

        env_data = {
            'dt': Ts,
            'system_dims': {
                "Inputs": system_dims["Inputs"],
                "Outputs": system_dims["Outputs"],
            }
        }
        self.scenarios = eval_scenario_descriptions(self.env_path, env_data)
        self.blocks = [self.reference] + self.plants + self.ctls

    def get_scenarios(self):
        return self.scenarios

    def select_scenario(self, index: int):
        if index < 0 or index >= len(self.scenarios):
            raise IndexError("Scenario index out of range.")
        self.set_scenario(self.scenarios[index])
        return self.scenarios[index]

    def compile(self):
        self.d.compile()
        self.d.report_lists()


    def run(self, T: float):
        out = self.sim.run(self.d, T=T, dt=self.Ts, watch=self._watchers)
        return SimOutput(out, watch_map=self._watch_map)

    def set_scenario(self, scenario):
        self.reference.set_data(scenario["Reference"][:, 0], scenario["Reference"][:, 1:])

        for i, plant_noise in enumerate(self.plant_noise_blocks):
            d = scenario.get("Disturbance", None)
            noise_obj = None
            sys_dims = plant_noise.system_dims
            if d is None or not d:
                info = self.backend.get_plugin_info_from_lib("NoNoise", 'csbenchlab')
                dist_class = get_plugin_class_from_info(info)
                noise_obj = dist_class('Params', {}, 'SystemDims', sys_dims)
            else:
                info = self.backend.get_plugin_info_from_lib(d["PluginName"], d["Lib"])
                dist_class = get_plugin_class_from_info(info)
                d_params = eval_plugin_params(self.env_path, d)
                noise_obj = dist_class('Params', d_params, 'SystemDims', sys_dims)
            noise_obj.configure()
            plant_noise.obj = noise_obj

        for plant in self.plants:
            plant.obj.configure(np.array(scenario["SystemIc"]))

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

    def import_component_module(self, comp_desc):
        cls_name = comp_desc["PluginName"]
        info = self.backend.get_plugin_info_from_lib(comp_desc["PluginName"], comp_desc["Lib"])
        module_path = info["ComponentPath"]
        if module_path not in self._module_classes:
            module = import_module_from_path(module_path)
            if not hasattr(module, cls_name):
                raise ValueError(f"Component class '{cls_name}' not found in module '{module_path}'.")
            self._module_classes[comp_desc["Id"]] = getattr(module, cls_name)

    def import_component_modules(self, comp_descriptions):
        for comp_desc in comp_descriptions.values():
            if not isinstance(comp_desc, list):
                comp_desc = [comp_desc]
            for comp_desc in comp_desc:
                self.import_component_module(comp_desc)

