import sys, os
file_name = sys.argv[0]
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file_name))))

from argparse import ArgumentParser
from pathlib import Path
import json5, json
import numpy as np
from csbenchlab.environment_data_manager import EnvironmentDataManager
from csbenchlab.plugin_helpers import import_module_from_path
from csbenchlab.helpers.metric_helpers import LiveMetricBase
import scipy.io as sio
from types import SimpleNamespace


def eval_function(func, *args):
    if hasattr(func, 'external_function__'):
        return {
            "external_function__": True,
            "function": func.external_function__,
            "backend": func.external_backend__,
            "kwargs": getattr(func, 'external_kwargs__', { }),
        }
    else:
        return func(*args)

def eval_metric(metric, sim_results):
    try:
        results_eval = eval_function(metric.metric, sim_results)
    except Exception as e:
        raise ValueError(f"Error evaluating 'metric'" +
                         f" function in '{metric.file_path}' for scenario '{metric['Id']}'" + f": {e}")

    return results_eval

def load_metrics(env_data_or_path):
    if isinstance(env_data_or_path, str):
        env_manager = EnvironmentDataManager(env_data_or_path)
        metrics = env_manager.get_components('metric')
        env_path = env_data_or_path
    else:
        metrics = env_data_or_path.metrics
        env_path = env_data_or_path.env_path

    loaded_metrics = SimpleNamespace(live_metrics = [], post_metrics = [])
    for m in metrics:
        metric_path = Path(env_path) / 'parts' / 'metrics' / m['Id']
        if not metric_path.exists():
            raise ValueError(f"Metric path '{metric_path}' does not exist for scenario '{m['Id']}'")
        metric_file = metric_path / 'metric.py'

        metric_module = import_module_from_path(metric_file) if metric_file.exists() else None
        if metric_module is None or not hasattr(metric_module, 'metric'):
            raise ValueError(f"'metric' function not defined in '{metric_file}' for scenario '{m['Id']}'")

        metric = SimpleNamespace(metric=metric_module.metric, file_path=str(metric_file))
        # check if it is a class first
        if isinstance(metric_module.metric, type) and issubclass(metric_module.metric, LiveMetricBase):
            loaded_metrics.live_metrics.append(metric)
        elif callable(metric_module.metric):
            loaded_metrics.post_metrics.append(metric)
        else:
            raise ValueError(f"'metric' in '{metric_file}' is neither callable nor a 'LiveMetricBase' subclass for scenario '{m['Id']}'")
    return loaded_metrics


def eval_metrics(metrics, env_results_or_path):
    if isinstance(env_results_or_path, str):
        sim_results = sio.loadmat(env_results_or_path)
    else:
        sim_results = env_results_or_path

    results = []
    for m in metrics:
        results_eval = eval_metric(m, sim_results)
        if not isinstance(results_eval, dict):
            raise ValueError(f"Metric evaluation did not return a dictionary, got {type(results_eval)}")
        results.append(results_eval)

    return json.dumps(results, indent=4)


def eval_environment_metrics(env_data_or_path, env_results_or_path):
    # eval metrics only works on post metrics
    loaded_metrics = load_metrics(env_data_or_path).post_metrics
    results = eval_metrics(loaded_metrics, env_results_or_path)
    return json.dumps(results, indent=4)


if __name__ == "__main__":

    parser = ArgumentParser(description="Get information about a specific plugin.")
    parser.add_argument("--env-path", type=str, default="", help="Path to the environment directory.")
    parser.add_argument("--results-path", type=str, default="", help="Path to the environment results file.")
    args = parser.parse_args()
    env_path = args.env_path
    if not env_path or not os.path.exists(env_path):
        raise ValueError(f"Environment path '{env_path}' does not exist.")

    results_path = args.results_path
    if not results_path or not os.path.exists(results_path):
        raise ValueError(f"Results path '{results_path}' does not exist.")

    result = eval_environment_metrics(env_path, results_path)