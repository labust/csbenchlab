
from argparse import ArgumentParser
from csbenchlab.backend.python_backend import PythonBackend
from csbenchlab.scenario_templates.control_environment import ControlEnvironment

from bdsim import BDSim

def main():

    parser = ArgumentParser(description="Component Debugger")
    parser.add_argument('--env-path', type=str, required=True, help="Path to the component to debug.")

    args = parser.parse_args()
    backend = PythonBackend()

    env_params, data = backend.generate_control_environment(args.env_path)

    env = ControlEnvironment(args.env_path, data.metadata, backend=backend)

    env.generate({
        "system": data.systems[0],
        "controllers": data.controllers
    }, env_params=env_params, generate_scopes=True)

    env.select_scenario(0)
    env.compile()
    return env.run(T=5.0, watch=plants)







if __name__ == "__main__":
    main()