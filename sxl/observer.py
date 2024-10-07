from sxl import spacetime

DEFAULT_DT = 0.001

class Observer:

    metric_tensor: spacetime.MetricTensor = None
    zero: spacetime.GeneralFourVector = None
    position: spacetime.GeneralFourVector = None # Current position
    velocity: spacetime.GeneralFourVector = None # Current linear velocity
    angular_position: spacetime.GeneralFourVector = None # Current angular position
    angular_velocity: spacetime.GeneralFourVector = None # Current angular velocity

    def __init__(self, metric: spacetime.MetricTensor, xi=None, vi=None, ti=None, wi=None):
        self.metric_tensor = metric
        self.zero = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
        self.position = xi if xi is not None else self.zero
        self.velocity = vi if vi is not None else self.zero
        self.angular_position = ti if ti is not None else self.zero
        self.angular_velocity = wi if wi is not None else self.zero

    def accelerate(self, acceleration: spacetime.GeneralFourVector, dt=DEFAULT_DT):
        self.velocity += acceleration * dt

    def translate(self, dt=DEFAULT_DT):
        self.position += self.velocity * dt

    def spin(self, acceleration: spacetime.GeneralFourVector, dt=DEFAULT_DT):
        self.angular_velocity += acceleration * dt
    
    def rotate(self, dt=DEFAULT_DT):
        self.angular_position += self.angular_velocity * dt

class ObserverEnsemble:

    observers: list[Observer] = None

    def __init__(self, *args, **kwargs):
        if args == [] and kwargs == {}:
            return
        raise SyntaxError("Please initialize ObserverEnsemble with .collect() and .make() class methods.")
    
    @classmethod
    def collect(cls, *observers):
        result = cls()
        if type(observers[0]) == list:
            observers = observers[0]
        result.observers = observers

    @classmethod
    def make(cls, positions, velocities, angular_positions, angular_velocities):
        if len(set(map(len, [positions, velocities, angular_positions, angular_velocities]))) > 1:
            raise SyntaxError("Invalid arguments. Use the same number of X, V, T, and W elements.")