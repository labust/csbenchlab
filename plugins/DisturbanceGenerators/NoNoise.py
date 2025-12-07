from csbenchlab.plugin import DisturbanceGenerator


class NoNoise(DisturbanceGenerator):

    def on_step(self, y, dt):
        return y