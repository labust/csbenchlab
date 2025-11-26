
from argparse import ArgumentParser
from backend.python_backend import PythonBackend
from csbenchlab.scenario_templates.control_environment import ControlEnvironment
from m_scripts.eval_scenario_descriptions import eval_scenario_descriptions

from bdsim import BDSim

def main():


    parser = ArgumentParser(description="Component Debugger")
    parser.add_argument('--env-path', type=str, required=True, help="Path to the component to debug.")

    args = parser.parse_args()
    backend = PythonBackend()

    env_params, data = backend.generate_control_environment(args.env_path)
    dims = backend.get_system_dims(data.systems[0], env_params[data.systems[0]['Id']])

    env = ControlEnvironment(data.metadata.get("Name", "GeneratedEnvironment"), backend=backend)
    sim = BDSim()

    d = sim.blockdiagram(env.env_name)

    env_data = {
        'dt': data.metadata['Ts'],
        'system_dims': {
            "Inputs": dims["Inputs"],
            "Outputs": dims["Outputs"],
        }
    }
    desc = eval_scenario_descriptions(args.env_path, env_data)


    env.generate({
        "system": data.systems[0],
        "controllers": data.controllers
    }, env_params=env_params, blockdiagram=d, Ts=data.metadata["Ts"], system_dims=dims)

    env.set_scenario(desc[0])

    d.compile()  # check the diagram
    d.report_lists()  # list all blocks and wires
    out = sim.run(d, dt=data.metadata["Ts"], T=5.0)
    return d







if __name__ == "__main__":
    main()