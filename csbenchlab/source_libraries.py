import sys
from pathlib import Path



def source_libraries(backend=None):
    if backend is None:
        from csbenchlab.csb_app_setup import get_backend
        backend = get_backend()
    for lib in backend.list_component_libraries():
        sys.path.append(lib)
        # n = Path(lib).name
        # sys.p
