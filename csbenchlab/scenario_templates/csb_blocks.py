from bdsim import BDSim, SourceBlock, EventSource, ClockedBlock, TransferBlock
import numpy as np

class Reference(SourceBlock, EventSource):
    def __init__(self, **blockargs):
        inames = []
        onames = ['y_ref']
        self.nout = len(onames)
        self.nin = len(inames)
        SourceBlock.__init__(self, inames=inames, onames=onames, **blockargs)


    def set_data(self, t, points):
        self.t = t
        self.y = points

    def output(self, t, inports, x):
        i = sum([1 if t >= _t else 0 for _t in self.t]) - 1
        out = self.y[i]
        return [out]



class PlantBlock(ClockedBlock):

    def __init__(self, clock, info, obj, dims, **blockargs):
        self.info = info
        self.dims = dims
        self.obj = obj
        inames = ['u', 't', 'dt']
        onames = ['y']
        self.nout = len(onames)
        self.nin = len(inames)
        self._x0 = []
        ClockedBlock.__init__(self, clock=clock, inames=inames, onames=onames, **blockargs)

    def set_ic(self, ic):
        self.setstate(np.array(ic))


    def output(self, t, u, x):
        return [self.obj.last_el]


    def next(self, t, inputs, x):
        xnext = self.obj.step(*inputs)
        return xnext


class ControllerBlock(ClockedBlock):


    def __init__(self, clock, info, obj, **blockargs):
        self.info = info
        self.obj = obj
        inames = ['y_ref', 'y', 'dt']
        onames = ['u', 'log']
        self.nout = len(onames)
        self.nin = len(inames)
        self._x0 = []
        ClockedBlock.__init__(self, clock=clock, inames=inames, onames=onames, **blockargs)


    def output(self, t, u, x):
        return [self.obj.last_el, []]

    def next(self, t, u, x):
        u_next = self.obj.step(*u)
        return u_next