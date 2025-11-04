from pathlib import Path
import json, json5


def load_env_controllers(env_path):
    controllers = []
    controllers_path = Path(env_path) / 'parts' / 'controllers'
    for controller_dir in controllers_path.iterdir():
        if not controller_dir.is_dir():
            continue
        controller_id = controller_dir.name
        controller_file = controller_dir / f"controller.json"
        if not controller_file.exists():
            continue
        with open(controller_file, 'r') as f:
            controller_info = json5.load(f)
            controllers.append(controller_info)
    return controllers