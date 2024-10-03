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
        self.coordinate_velocity = initialVelocity \
        if initialVelocity is not None \
        else spacetime.GeneralFourVector.zero(self.metric)
        

class ObserverEngine:
