from sxl import spacetime

class Observer:

    metric: spacetime.MetricTensor
    position: spacetime.GeneralFourVector = None
    coordinate_velocity: spacetime.GeneralFourVector = None

    def __init__(self,
                metric: spacetime.MetricTensor,
                initialPosition: spacetime.GeneralFourVector,
                initialVelocity: spacetime.GeneralFourVector=None):
        self.metric = metric
        self.position = initialPosition
        if initialVelocity is not None:
            self.coordinate_velocity = initialVelocity
        else:
            self.coordinate_velocity = spacetime.GeneralFourVector.zero(self.metric)