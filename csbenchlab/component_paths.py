from pathlib import Path

STANDALONE_COMPONENT_PATHS = {
    'controller': (Path('parts') / 'controllers', 'controller.json'),
    'system': (Path('parts') / 'systems', 'system.json'),
    'scenario': (Path('parts') / 'scenarios', 'scenario.json'),
    'metric': (Path('parts') / 'metrics', 'metric.json'),
    'metadata': (Path('config.json'), None)
}