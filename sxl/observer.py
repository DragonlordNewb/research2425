from sxl import spacetime
from math import sqrt

DT = 0.001

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

	def compute_lorentz_factor(self):
		"""
		c^2 dtau^2 = g_ij dx^i dx^j = g_ij v^i v^j dt^2
		[v^i = dx^i/dt  and  v^0 = dt/dt = 1]

	 -> dt/dtau = sqrt(c^2 / g_ij v^i v^j) = sqrt(1 / 1 - g_ab v^a v^b)
		since g_tt v^t v^t = c^2 * 1 * 1 = c^2.

		Finding the coordinate velocity from the proper velocity
		is the hard part here. We do have the relation

		gamma = cosh(arcsinh(w/c))

		to help us out here, though. TO DO: check that this holds
		in curved spacetime as well as in flat spacetime! I would
		think that it does by dint of the nature of gamma and all
		of hyperbolic geometry, 
		"""

		wi = [
			self.proper_velocity[1], 
			self.proper_velocity[2],
			self.proper_velocity[3]
		]
		w = sqrt(sum((wi[i] for i in range(3))))
		self.proper_velocity[0] = 


	def lorentz_factor(self):
		return self.proper_velocity.u(0)
	
	"""
	This is probably an abuse of the word "speed" but it's
	more compact than "spatial_velocity". I hope you get my
	meaning here.
	"""

	def proper_speed(self):
		return sqrt(
			self.proper_velocity[1]**2 \
			+ self.proper_velocity[2]**2 \
			+ self.proper_velocity[3]**2
		)
	
	def coordinate_speed(self):
		return sqrt(
			self.coordinate_velocity[1]**2 \
			+ self.coordinate_velocity[2]**2 \
			+ self.coordinate_velocity[3]**2
		)

	def apply_proper_acceleration(self, a: spacetime.GeneralFourVector, dtau: float=DT):
		"""
		Update proper velocity based on proper acceleration:
		du = d(dX/dtau) = alpha dtau = (d^2X/dtau^2)dtau.
		"""
		self.proper_velocity += a * dtau

	def apply_coordinate_acceleration(self, a: spacetime.GeneralFourVector, dt: float=DT):
		"""
		Update proper velocity based on coordinate acceleration:
		du = d(dX/dtau) = a gamma^3 dtau = (d^2X/dt^2)(dt/dtau)^3 dtau.
		"""
		self.proper_velocity += a * self.lorentz_factor()**3 * dt

	def apply_proper_time(self, dtau: float=DT):
		"""
		Update coordinate position based on elapsed proper time:
		dX = u dtau = (dX/dtau)dtau.

		Additionally tracks proper time lapses.
		"""
		self.position += self.proper_velocity * dtau
		self.proper_time_lapse += dtau

	def apply_coordinate_time(self, dt: float=DT):
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
						  either .collect(), .make(), or .merge().")

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

	def add_observer(self, observer: Observer) -> int:
		self.observers.append(observer)
		return len(self) - 1

	def remove_observer(self, index: int):
		self.observers.remove(index)
	
	def lorentz_factors(self) -> list[float]:
		"""
		Return a list of the Lorentz factors of the observers.
		"""
		result = []
		for observer in self:
			result.append(observer.lorentz_factor())
		return result
	
	def apply_proper_acceleration(self, a: spacetime.GeneralFourVector, dtau: float=DEFAULT_DT):
		"""
		Apply a proper acceleration to all observers.
		"""
		for observer in self:
			observer.apply_proper_acceleration(a, dtau)
	
	def apply_coordinate_acceleration(self, a: spacetime.GeneralFourVector, dt: float=DEFAULT_DT):
		"""
		Apply a coordinate acceleration to all observers.
		"""
		for observer in self:
			observer.apply_coordinate_acceleration(a, dt)

	def apply_proper_time(self, dtau=DEFAULT_DT):
		for observer in self:
			observer.apply_proper_time(dtau)

	def apply_coordinate_time(self, dt=DEFAULT_DT):
		for observer in self:
			observer.apply_coordinate_time(dt)

	# Maker classes

	@classmethod
	def collect(cls, *observers):
		result = cls()
		cls.observers = observers
	
	@classmethod
	def make(cls, xis, vis, tis, wis):
		l = len(xis)
		if l != len(vis) or l != len(tis) or l != len(wis):
			raise SyntaxError("Invalid inputs to .make(). Must be lists of GFVs of the same length.")
		
		result = cls()
		for i in range(l):
			result.add_observer(Observer(xis[i], vis[i], tis[i], wis[i]))
		return result
	
	@classmethod
	def merge(cls, *ensembles: "ObserverEnsemble") -> "ObserverEnsemble":
		result = cls()
		for ens in ensembles:
			for observer in ens:
				result.add_observer(observer)
		return result
	
class ObservationEngine:

	observer = None
	ensemble = None

	st: spacetime.Spacetime = None
	coordinates: spacetime.CoordinateSystem = None
	units: spacetime.UnitSystem = None

	def __init__(self, st: spacetime.Spacetime) -> None:
		self.st = st
		self.coordinates = self.st.coordinates 
		self.proper_acceleration_vector = st.geodesic_acceleration_vectors.proper_vector()
		self.coordinate_acceleration_vector = st.geodesic_acceleration_vectors.coordinate_vector()

	def proper_acceleration_vector_at(self, point: spacetime.GeneralFourVector):
		return self.st.evaluate(
			self.proper_acceleration_vector, point
		)

	def coordinate_acceleration_vector_at(self, point: spacetime.GeneralFourVector):
		return self.st.evaluate(
			self.coordinate_acceleration_vector, point
		)