from sxl import spacetime

DEFAULT_DT = 0.001

class Observer:

    metric_tensor: spacetime.MetricTensor = None
    zero: spacetime.GeneralFourVector = None
    proper_time_lapse: float = 0
    position: spacetime.GeneralFourVector = None # Current position, X (with coordinate time)
    proper_velocity: spacetime.GeneralFourVector = None # Current proper linear velocity, u=dX/dtau
    angle: spacetime.GeneralFourVector = None # Current angular position, theta
    proper_rotation: spacetime.GeneralFourVector = None # Current angular velocity, w=dtheta/dtau

    def __init__(self, metric: spacetime.MetricTensor, xi=None, vi=None, ti=None, wi=None):
        self.metric_tensor = metric
        self.zero = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
        self.position = xi if xi is not None else self.zero
        self.velocity = vi if vi is not None else self.zero
        self.angle = ti if ti is not None else self.zero
        self.proper_rotation = wi if wi is not None else self.zero

    def lorentz_factor(self):
        return self.proper_velocity.u(0)

    def apply_proper_acceleration(self, a: spacetime.GeneralFourVector, dtau: float):
        """
        Update proper velocity based on proper acceleration:
        du = d(dX/dtau) = alpha dtau = (d^2X/dtau^2)dtau.
        """
        self.proper_velocity += a * dtau

    def apply_coordinate_acceleration(self, a: spacetime.GeneralFourVector, dt: float):
        """
        Update proper velocity based on coordinate acceleration:
        du = d(dX/dtau) = a gamma^3 dtau = (d^2X/dt^2)(dt/dtau)^3 dtau.
        """
        self.proper_velocity += a * self.lorentz_factor()**3 * dt

    def apply_proper_time(self, dtau: float):
        """
        Update coordinate position based on elapsed proper time:
        dX = u dtau = (dX/dtau)dtau.

        Additionally tracks proper time lapses.
        """
        self.position += self.proper_velocity * dtau
        self.proper_time_lapse += dtau

    def apply_coordinate_time(self, dt: float):
        """
        Update coordinate position based on elapsed coordinate time:
        dX = u dt/gamma = (dX/dtau)(dtau/dt) dt.

        Additionally tracks proper time lapses:
        dtau = dt / gamma = dt / (dt/dtau) = (dtau/dt)dt.
        """
        self.position += self.proper_velocity * dt / self.lorentz_factor()
        self.proper_time_lapse += dt / self.lorentz_factor()

class ObserverEnsemble:

    observers = []
    _n = 0

    def __init__(self, *args, **kwargs):
        if len(kwargs.keys()) == len(args) == 0:
            return
        raise SyntaxError("ObserverEnsemble must be initialized with \
                          either .collect() or .make().")

    def __len__(self):
        return len(self.observers)

    def __iter__(self):
        self._n = -1
        return self

    def __next__(self):
        self._n += 1
        if self._n >= len(self):
            raise StopIteration
        return self.observers[self._n]

    def __getitem__(self, i: int):
        return self.observers[i]
    
    def lorentz_factors(self) -> list[float]:
        """
        Return a list of the Lorentz factors of the observers.
        """
        result = []
        for observer in self:
            result.append(observer.lorentz_factor())
        return result
    
    def apply_proper_acceleration(self, a: spacetime.GeneralFourVector, dtau: float):
        """
        Apply a proper acceleration to all observers.
        """
        for observer in self:
            observer.apply_proper_acceleration(a, dtau)
    
    def apply_coordinate_acceleration(self, a: spacetime.GeneralFourVector, dt: float):
        """
        Apply a coordinate acceleration to all observers.
        """
        for observer in self:
            observer.apply_coordinate_acceleration(a, dt)

    def apply_proper_time(self, dtau):
        for observer in self:
            observer.apply_proper_time(dtau)

    def apply_coordinate_time(self, dt):
        for observer in self:
            observer.apply_coordinate_time(dt)