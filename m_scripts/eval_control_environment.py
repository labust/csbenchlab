from argparse import ArgumentParser
from csbenchlab.backend.python_backend import PythonBackend
from csbenchlab.scenario_templates.control_environment import ControlEnvironment
from m_scripts.eval_metrics import eval_metrics
from bdsim import BDSim


def eval_control_environment(env_path, system_instance:str=None, controller_ids:str=None):
    backend = PythonBackend()
    env_params, data = backend.load_control_environment_params_and_data(env_path, system_instance, controller_ids)

    env = ControlEnvironment(env_path, data.metadata, backend=backend)

    plants = env.generate({
        "system": data.systems[0],
        "controllers": data.controllers
    }, env_params=env_params, generate_scopes=False)

    env.select_scenario(0)
    env.compile()
    out = env.run(T=5.0, watch=plants)


    r = eval_metrics(data, out)
    print(r)


def main():

    {{env_path}}

    args = parser.parse_args()

    eval_control_environment(args.env_path)

if __name__ == "__main__":
    main()