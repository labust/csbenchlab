import numpy as np
from math import ceil
from csbenchlab.common_types import *
from csbenchlab.sim_output import SimOutput


import numpy as np
import matplotlib.pyplot as plt

def is_valid_field(params, key):
    return params is not None and key in params and params[key] is not None

def out_with_ref(out: SimOutput, ref_dimensions=[], out_dimensions=[],
                 controllers=[], grid=None, name=None, f_handle=None,
                 linewidth=1, axis=None, position=None, xlabel=None, ylabel=None, legend=None):
    # Figure handle
    if f_handle is None:
        f = plt.figure()
        ax = f.gca()
    else:
        f = f_handle
        ax = f.gca()

    # Grid
    if grid is not None:
        ax.grid(True)  # [web:16]

    # "Name" => figure window title (if backend supports it)
    if name is not None:
        try:
            f.canvas.manager.set_window_title(name)  # [web:13][web:19]
        except Exception:
            pass

    # Reference dimensions
    if ref_dimensions:
        ref_dims = np.array(ref_dimensions, dtype=int)
    else:
        ref_dim = out.ref.Data.shape[1]
        ref_dims = np.arange(ref_dim)  # 0-based for NumPy [web:9]

    # Output dimensions
    if out_dimensions:
        out_dims = np.array(out_dimensions, dtype=int)
    else:
        # Take first field in out.y
        first_key = next(iter(out.y.keys()))
        out_dim = out.y[first_key].Data.shape[1]
        out_dims = np.arange(out_dim, dtype=int)  # [web:9]

    # Plot reference (dashed)
    ax.plot(out.ref.Time, out.ref.Data[:, ref_dims], linewidth=linewidth, linestyle="--")

    # Controller names
    if controllers is not None and len(controllers) > 0:
        names = controllers
    else:
        names = list(out.y.keys())

    # Plot each controller output
    for n in names:
        data_obj = out.y[n]
        data = data_obj.Data
        sz = data.shape

        # Emulate the MATLAB sz(end) == length(data.Data) logic
        # Here assume data is either (len(time), ny) or (ny, len(time), ...)
        if sz[-1] == data.shape[0]:
            # MATLAB: squeeze(data.Data(out_dims, :, :))
            sliced = np.squeeze(data[out_dims, ...])
            # Ensure time is last dim for plotting
            if sliced.ndim == 1:
                ax.plot(data_obj.Time, sliced, linewidth=linewidth)
            else:
                ax.plot(data_obj.Time, sliced.T, linewidth=linewidth)  # each row a series
        else:
            # MATLAB: squeeze(data.Data(:, out_dims))
            sliced = np.squeeze(data[:, out_dims])
            if sliced.ndim == 1:
                ax.plot(data_obj.Time, sliced, linewidth=linewidth)
            else:
                ax.plot(data_obj.Time, sliced, linewidth=linewidth)

    # Axis limits
    if axis is not None:
        ax.axis(axis)

    # Figure position (best-effort, depends on backend)
    if position is not None:
        try:
            mng = plt.get_current_fig_manager()
            x, y, w, h = position
            mng.window.setGeometry(int(x), int(y), int(w), int(h))
        except Exception:
            pass

    # Labels
    if xlabel is not None:
        ax.set_xlabel(xlabel)  # [web:16]
    if ylabel is not None:
        ax.set_ylabel(ylabel)  # [web:16]

    # Legend
    if legend is not None:
        ax.legend(*legend)
    else:
        leg_names = []
        # Reference labels
        for i in range(len(ref_dims)):
            leg_names.append(f"Reference_{i+1}")
        # Output labels
        fns = list(out.y.keys())
        for name in fns:
            for j in range(len(out_dims)):
                leg_names.append(f"{name}_{j+1}")
        ax.legend(leg_names)

    return f, ax
