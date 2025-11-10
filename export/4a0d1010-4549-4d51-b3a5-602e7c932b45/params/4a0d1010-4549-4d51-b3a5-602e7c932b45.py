
from dataclasses import dataclass, field
from typing import List, Dict, Any
from csbenchlab.common_types import LoadFromFile, PyFunctionHandle, MatFunctionHandle
import numpy as np

@dataclass
class ComponentParams:
    payload_mass: int = 5.1
    payload_location: Any = np.array([0, 0, 0])
    current_speed: int = 0
    current_direction: int = 0
    out_gain: int = 1
