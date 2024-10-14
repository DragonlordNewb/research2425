from sxl import spacetime
from sympy import *
from math import *
from abc import *

DT = 0.001

TIMELIKE = "TIMELIKE"
LIGHTLIKE = "LIGHTLIKE"
SPACELIKE = "SPACELIKE"

# ===== WORLDLINES ===== #

class Observer:

	units: spacetime.UnitSystem = None
	metric_tensor: spacetime.MetricTensor = None
	zero: spacetime.GeneralFourVector = None
	proper_time_lapse: float = 0
	position: spacetime.GeneralFourVector = None # Current position, X (with coordinate time)
	proper_velocity: spacetime.GeneralFourVector = None # Current proper linear velocity, u=dX/dtau
	angle: spacetime.GeneralFourVector = None # Current angular position, theta
	proper_rotation: spacetime.GeneralFourVector = None # Current angular velocity, w=dtheta/dtau
	couplings: dict[Symbol] = None # Couplings to fields (see FIELDS)
	mass: float = None

	def __init__(self, metric: spacetime.MetricTensor, xi=None, vi=None, ti=None, wi=None, mass=None, **couplings):
		self.units = metric.units
		self.metric_tensor = metric
		self.zero = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
		self.position = xi if xi is not None else self.zero
		self.velocity = vi if vi is not None else self.zero
		self.angle = ti if ti is not None else self.zero
		self.proper_rotation = wi if wi is not None else self.zero
		self.couplings = {Symbol(cc): couplings[cc] for cc in couplings.keys()}
		if "m" in self.couplings.keys():
			self.mass = self.coupling("m")
		elif mass is not None:
			self.mass = mass
			self.couplings[Symbol("m")] = mass
		else:
			raise SyntaxError("Mass must be somehow specified for an Observer.")

	def coupling(self, target: str | Symbol):
		for coupling in self.couplings.keys():
			if coupling.name == target or coupling == target:
				return coupling
		return 0

	def compute_lorentz_factor(self):
		"""
		c^2 dtau^2 = g_ij dx^i dx^j = g_ij v^i v^j dt^2
		[v^i = dx^i/dt  and  v^0 = dt/dt = 1]

	 -> dt/dtau = sqrt(c^2 / g_ij v^i v^j) = sqrt(1 / 1 - g_ab v^a v^b)
		
		since g_tt v^t v^t = c^2 * 1 * 1 = c^2.

		Finding the coordinate velocity from the proper velocity
		is the hard part here. We do have the relation

		gamma = cosh(arcsinh(w/c)) = 1 / sqrt(1 - w^2/c^2)

		to help us out here, though.
		"""

		wi = [
			self.proper_velocity[1], 
			self.proper_velocity[2],
			self.proper_velocity[3]
		]
		w = sqrt(sum((wi[i] for i in range(3))))
		lorentz = 1 / sqrt(1 - (w**2 / self.units.c**2))
		self.proper_velocity.vector_u[0] = lorentz
		return lorentz

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
		self.proper_velocity += a * self.compute_lorentz_factor()**3 * dt

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
		self.position += self.proper_velocity * dt / self.compute_lorentz_factor()
		self.proper_time_lapse += dt / self.compute_lorentz_factor()

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
			result.append(observer.compute_lorentz_factor())
		return result
	
	def apply_proper_acceleration(self, a: spacetime.GeneralFourVector, dtau: float=DT):
		"""
		Apply a proper acceleration to all observers.
		"""
		for observer in self:
			observer.apply_proper_acceleration(a, dtau)
	
	def apply_coordinate_acceleration(self, a: spacetime.GeneralFourVector, dt: float=DT):
		"""
		Apply a coordinate acceleration to all observers.
		"""
		for observer in self:
			observer.apply_coordinate_acceleration(a, dt)

	def apply_proper_time(self, dtau=DT):
		for observer in self:
			observer.apply_proper_time(dtau)

	def apply_coordinate_time(self, dt=DT):
		for observer in self:
			observer.apply_coordinate_time(dt)

	# Maker classes

	@classmethod
	def collect(cls, *observers):
		result = cls()
		cls.observers = observers
	
	@classmethod
	def make(cls, xis, vis, tis, wis, masses, couplings):
		l = len(xis)
		if l != len(vis) or l != len(tis) or l != len(wis):
			raise SyntaxError("Invalid inputs to .make(). Must be lists of GFVs of the same length.")
		
		result = cls()
		for i in range(l):
			result.add_observer(Observer(xis[i], vis[i], tis[i], wis[i], masses[i], couplings[i]))
		return result
	
	@classmethod
	def merge(cls, *ensembles: "ObserverEnsemble") -> "ObserverEnsemble":
		result = cls()
		for ens in ensembles:
			for observer in ens:
				result.add_observer(observer)
		return result
	
class Geodesic:

	x: spacetime.GeneralFourVector
	v: spacetime.GeneralFourVector
	ds2: Symbol
	geodesic_t = None
	metric_tensor: spacetime.MetricTensor = None
	units: spacetime.UnitSystem = None

	def __init__(self, xi, vi, ds2, metric: spacetime.MetricTensor) -> None:
		self.x = xi
		self.v = vi
		self.ds2 = ds2
		if self.ds2 < 0:
			self.geodesic_t = SPACELIKE
		if self.ds2 == 0:
			self.geodesic_t = LIGHTLIKE
		if self.ds > 0:
			self.geodesic_t = TIMELIKE
		self.metric_tensor = metric
		self.units = self.metric_tensor.units

	def geodesic_type(self):
		return self.geodesic_t

class NullGeodesic(Geodesic):

	def __init__(self, xi, vi):
		Geodesic.__init__(self, xi, vi, 0)
	
# ===== FIELDS ===== #

class Field(ABC):

	"""
	The most general Field class. Simply
	exists to allow subclassing into more-
	precise fields that can actually be
	used.

	The Field.specific_proper_force() method is
	intended to be called once in-place to
	fill the Field.specific_force 4-vector with the 
	correct values.
	"""

	coupling_constant: Symbol = None
	
	@abstractmethod
	def specific_proper_force(self, observer: Observer) -> None:
		raise NotImplemented("Field.specific_proper_force() is not implemented. Use a fully-defined Field subclass.")
	
class ForceField(Field):

	def __init__(self, f: spacetime.GeneralFourVector):
		self.specific_force = f

	def specific_proper_force(self, observer: Observer) -> None:
		return self.specific_force

# === Bosonic Fields === #

class SpinningBosonField(Field):

	"""
	A field with a nonzero integer spin
	(in practice, either 1 or 2). So differentiated
	from a non-spinning boson field (spin 0) because
	such fields do not typically impart force when
	static or otherwise unperturbed.

	In this case, we have an additional subclass
	because the fields we're describing have the
	property that the force that they put on
	particles is given by

	(spin 1) f^i = g T^ij v_j
	(spin 2) f^i = g T^ijk v_j v_k / f^i = g T^i_jk v^j v^k

	for "effective tensors" T. Technically, these
	tensors can end up having more indices than
	the field has spin (like in the case of the
	QCD gluon field strength tensor, which has 
	three indices - two "regular" indices and one
	ranging from 1 to 8 referring to the eight
	color charge configurations), and in this case
	the "effective" tensor is a contraction of that
	tensor with the appropriate vector/tensor (in
	the case of the QCD GFS tensor, the color 
	charge profiles).

	For the EM field, the effective tensor is the
	Faraday/EM tensor. For the strong field, the
	effective tensor is the charge-contracted
	QCD GFS tensor. For the gravitational field,
	the effective tensor is, unsurprisingly, the
	Christoffel symbol of the second kind.
	"""

	# coupling_constant
	# def specific_proper_force(self, observer: Observer) -> None

	effective_tensor: spacetime.GeneralTensor = None

class VectorField(SpinningBosonField):

	"""
	The VectorField class, describing
	exactly that.

	Allows calculation of forces from a vector
	field, where the force equation is simple
	enough.
	"""

	# coupling_constant
	# effective_tensor

	vector: spacetime.GeneralFourVector = None
	metric_tensor: spacetime.MetricTensor = None
	coordinates: spacetime.CoordinateSystem = None
	
	@abstractmethod
	def compute_effective_tensor(self) -> None:
		raise NotImplemented("SpinningBosonField.compute_effective_tensor() is not implemented. Use a fully-defined SpinningBosonField subclass.")

	def specific_proper_force(self, observer) -> Symbol:
		"""
		f^i = g F^ij u_j = g F^i_j u^j
		"""
		self.compute_effective_tensor()
		f = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
		for i in range(4):
			fi = 0
			for j in range(4):
				fi = fi + (self.effective_tensor.uu(i, j) * observer.proper_velocity.d(j))
			f.vector_u[i] = fi
		f.compute()
		return f

class AbelianVectorField(VectorField):

	"""
	The AbelianVectorField class, describing
	exactly that.

	Allows calculation of forces from a vector
	field where the effective tensor (see the
	SpinningBosonField superclass) is just the
	commutator of the underlying vector field.
	"""

	# coupling_constant
	# effective_tensor
	# vector
	# metric_tensor
	# coordinates

	def __init__(self, vector: spacetime.GeneralFourVector) -> None:
		self.vector = vector
		self.metric_tensor = self.vector.metric_tensor
		self.coordinates = self.metric_tensor.coordinates

	def compute_effective_tensor(self):
		if self.effective_tensor is None:
			self.effective_tensor = spacetime.GeneralRankTwoTensor(self.metric_tensor, "uu", spacetime.ANTISYMMETRIC)
			self.vector.compute()
			for i in range(4):
				for j in range(4):
					self.effective_tensor.tensor_dd[i, j] = self.vector.d(j).diff(self.coordinates.x(i)) - self.vector.d(i).diff(self.coordinates.x(j))
					self.effective_tensor.uu(i, j)

	# Examples

class NonAbelianVectorField(VectorField):

	# coupling_constant
	# effective_tensor
	# def compute_effective_tensor(self) -> None
	# vector
	# metric_tensor
	# coordinates

	"""
	The AbelianVectorField class, describing
	exactly that.

	Allows calculation of forces from a vector
	field where the effective tensor (see the
	SpinningBosonField superclass) is the 
	contraction over the group indices of a
	more-complicated rank-three tensor (two
	spacetime indices and one group indices),
	contracting with the profiles of the group.
	"""

	pass # ...for now. The strong and weak fields
	# need not be implemented for an accurate
	# macroscale (super-quantum) representation of
	# reality.

class TensorField(SpinningBosonField):

	"""
	The TensorField, describing exactly that.

	Allows calculation of forces from a tensor
	field where the force equation is analogous
	to the GAV in GR.
	"""

	# coupling_constant
	# effective_tensor

	def __init__(self, et: spacetime.GeneralRankThreeTensor):
		self.effective_tensor = et

	def specific_proper_force(self, observer: Observer) -> Symbol:
		"""
		f^i = g F^ijk u_j u_k = g F^i_jk u^j u^k
		"""
		f = spacetime.GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
		for i in range(4):
			fi = 0
			for j in range(4):
				for k in range(4):
					fi = fi + (self.effective_tensor.uuu(i, j, k) * observer.proper_velocity.d(j) * observer.proper_velocity.d(k))
			f.vector_u[i] = fi
		f.compute()
		return f

	# Examples

	@classmethod
	def graviton(cls, arg: "something that has a ChristoffelSymbols" | spacetime.MetricTensor):
		if type(arg) == spacetime.MetricTensor:
			cs = spacetime.ChristoffelSymbols(arg)
		else:
			# the assumption is that the passed argument
			# has a .metric_tensor or .christoffel_symbols
			# attribute
			if hasattr(arg, "christoffel_symbols"):
				cs = arg.christoffel_symbols
			elif hasattr(arg, "metric_tensor"):
				cs = spacetime.ChristoffelSymbols(arg.metric_tensor)
			else:
				raise SyntaxError("Invalid arguments to produce graviton field.")
		T = cs.to_r3_tensor()
		return cls(T)

# === Fermionic Fields === #

class SpinorField(Field):
	pass # ...spin 1/2 - not super interesting right now

class RaritaSchwingerField(Field):
	pass # ...spin 3/2 - not super interesting right now

class FieldTheory(Field):

	fields = []

	def __init__(self, *fields):
		self.fields = list(fields)
		for field in self:
			ft = type(field)
			if (not issubclass(ft, Field)) or (ft == Field):
				raise TypeError("FieldTheory only accepts Field subclasses as arguments.")

	def __iter__(self):
		return iter(self.fields)

	def proper_acceleration_on(self, observer: Observer) -> None:
		accel = 0
		for field in self:
			accel = accel + field.specific_proper_force(observer)/observer.mass
		return accel

# ===== THE OBSERVATION ENGINE ===== #

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