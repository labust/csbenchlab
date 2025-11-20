from bdsim import BDSim, SourceBlock, EventSource, ClockedBlock

class Reference(SourceBlock, EventSource):
    def __init__(self, **blockargs):
        SourceBlock.__init__(self, **blockargs)

    def configure(self, ref_info):
        pass

    def start(self, simstate):
        super().start(simstate)

        if simstate is not None:
            for t in self.t:
                simstate.declare_event(self, t)

    def output(self, t, inports, x):
        i = sum([1 if t >= _t else 0 for _t in self.t]) - 1
        out = self.y[i]
        # print(out)
        return [out]



class Plant(ClockedBlock):
    def __init__(self, **blockargs):
        ClockedBlock.__init__(self, **blockargs)

    def configure(self, plant_info):
        pass

    def output(self, t, inports, x):
        # print(inports[0])
        return [inports[0]]


class Controller(ClockedBlock):
    def __init__(self, **blockargs):
        ClockedBlock.__init__(self, **blockargs)

    def configure(self, controller_info):
        pass

    def output(self, t, inports, x):
        # print(inports[0])
        return [inports[0]]