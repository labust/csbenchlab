from pathlib import Path
from typing import Union

def is_env_path(env_path: Union[str, Path]) -> bool:
    p = Path(env_path)
    if not p.is_absolute():
        p = Path('.') / p
    name = p.stem
    return (p / f"{name}.cse").is_file()
