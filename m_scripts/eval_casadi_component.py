import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))
from argparse import ArgumentParser
from csbenchlab.source_libraries import source_libraries
import numpy as np
from csbenchlab.plugin_helpers import import_module_from_path
from pathlib import Path

def eval_casadi_component(plugin_path: str, results_path: str):

    class_name = Path(plugin_path).stem
    plugin_module = import_module_from_path(plugin_path)

    if not hasattr(plugin_module, class_name):
        raise ValueError(f"The plugin at '{plugin_path}' does not have a '{class_name}' class.")

    casadi_component = getattr(plugin_module, class_name)()

    # Here you would perform evaluations with the casadi_component
    # For demonstration, let's assume we just save some dummy results

    results = {
        "component_name": casadi_component.name,
        "evaluation_result": np.random.rand()  # Dummy evaluation result
    }

    results_file = os.path.join(results_path, "casadi_component_results.json")
    with open(results_file, 'w') as f:
        import json
        json.dump(results, f, indent=4)

    print(f"Results saved to {results_file}")


if __name__ == "__main__":

    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--plugin-path", type=str, default="", help="Path to the plugin.")
    parser.add_argument("--results-path", type=str, default="", help="Path where to store results.")
    args = parser.parse_args()

    source_libraries()

    if not os.path.exists(args.plugin_path):
        raise ValueError(f"Plugin path '{args.plugin_path}' does not exist.")

    if not os.path.exists(args.results_path):
        raise ValueError(f"Results path '{args.results_path}' does not exist.")


    eval_casadi_component(args.plugin_path, args.results_path)