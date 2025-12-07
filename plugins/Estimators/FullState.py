from csbenchlab.plugin import Estimator


class FullState(Estimator):

    def on_step(self, y, dt):
        return y