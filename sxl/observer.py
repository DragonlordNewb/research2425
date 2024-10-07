from sxl import spacetime

DEFAULT_DT = 0.001

class Observer:

    metric_tensor: spacetime.MetricTensor = None
    zero: spacetime.GeneralFourVector = None
    position: spacetime.GeneralFourVector = None # Current position
    velocity: spacetime.GeneralFourVector = None # Current linear velocity
    rotation: spacetime.GeneralFourVector = None # Current angular velocity

    def __init__(self, metric: spacetime.MetricTensor, xi=None, vi=None, wi=None):
        self.metric_tensor = metric
        self.zero = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
        self.position = xi if xi is not None else self.zero
        self.velocity = vi if vi is not None else self.zero
        self.rotation = wi if wi is not None else self.zero

    def tick(self, dt: float=DEFAULT_DT):
        pass