from csbenchlab.plugin import DynSystem, Controller
from typing import List
from csbenchlab.scenario_templates.csb_blocks import *
import bdsim as bd

class ControlEnvironment:

    @staticmethod
    def components():
        return {
            "system": DynSystem,
            "controllers": List[Controller]
        }

    def __init__(self, env_name: str):
        self.env_name = env_name
        self._components = {}

    def generate(self, comp_descriptions):
        self.generate_component_instances(comp_descriptions)

        sim = bd.BDSim()
        d = sim.blockdiagram(self.env_name)
        self.reference = Reference(name="Reference")
        d.add_block(self.reference)
        for i, controller in enumerate(self.controllers):
            name = comp_descriptions["system"]["Name"] + f"_Controller_{i+1}"
            plant = Plant(name=name)
            plant.configure(comp_descriptions["system"])
            d.add_block(plant)
            controller = Controller(name=name)
            controller.configure(comp_descriptions["controllers"][i])
            d.add_block(controller)

            d.connect(plant, "out", controller, "in")
            d.connect(controller, "out", plant, "in")

            d.connect(self.reference, "out", controller, "in")

        a = 5

