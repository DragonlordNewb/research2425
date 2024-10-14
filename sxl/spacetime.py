from sympy import *
from warnings import *
from abc import *
from typing import Union
from sxl.util import *
from sxl.error import *

simplefilter("ignore") # I don't care that SymPy doesn't want None in its matrices.

# ===== CONSTANTS ===== #

METRIC_DERIVATIVES = "metric derivatives"
CHRISTOFFEL_SYMBOLS = "christoffel symbols"
INDEX_RAISING = "index raising"
RIEMANN_UDDD_MODE = CHRISTOFFEL_SYMBOLS
PB_INDENT = 0

REAL_c = 299792458
REAL_G = 6.6743e-11
REAL_h = 6.62607015e-34
REAL_Lambda = 1.1056e-52

NO_SYMMETRY = None
SYMMETRIC = "symmetric"
ANTISYMMETRIC = "antisymmetric"

# ===== METRICS FOR SPACES ===== #

class UnitSystem:

	"""
	UnitSystem class.

	Contains information about the unit system.
	This is generally valuable because it allows
	consistency between c=G=1, c=c and G=G, and
	other systems of units, as well as stores info
	about whether or not the cosmological constant
	is to be considered.
	"""

	c = None
	G = None
	h = None
	Lambda = None
	kappa = None

	def __init__(self, normc, normG, normh, normLambda):
		self.c = 1 if normc else Symbol("c")
		self.G = 1 if normG else Symbol("G")
		self.h = 1 if normh else Symbol("h")
		self.Lambda = 0 if normLambda else Symbol("Lambda")
		self.kappa = Symbol("kappa") # 8 * pi * self.G / self.c**4

	# Implementations

	@classmethod
	def si(cls):
		"""
		The SI system of units (with a cosmological
		constant).
		"""
		return cls(False, False, False, False)
	
	@classmethod
	def si_ncc(cls):
		"""
		The SI system of units (without a 
		cosmological constant).
		"""
		return cls(False, False, False, True)

	@classmethod
	def natural(cls):
		"""
		The natural system of units (with a
		cosmological constant).
		"""
		return cls(True, True, True, False)

	@classmethod
	def natural_ncc(cls):
		"""
		The natural system of units (without
		a cosmological constant).
		"""
		return cls(True, True, True, True)

class CoordinateSystem:

	"""
	The CoordinateSystem class.
	
	Represents a 4-dimensional coordinate
	system. Automatically generates coordinate-
	time and proper-time derivatives of position
	for use later and stores the names of each
	coordinate as Symbols.
	"""

	dimensionality: int = 4
	dimensions: list[int] = [0, 1, 2, 3]
	coordinates: list[Symbol]
	differential_elements: list[Symbol]
	proper_time = Symbol("tau")
	coordinate_velocities: list[Symbol] = None
	proper_velocities: list[Symbol] = None
	_n = 0

	def __init__(self, x0, x1, x2, x3) -> None:
		self.coordinates = list(symbols(" ".join([x0, x1, x2, x3])))
		self.differential_elements = list(symbols(" ".join(["d" + i for i in [x0, x1, x2, x3]])))
		self.coordinate_velocities = list(symbols(" ".join(["v_" + i for i in [x0, x1, x2, x3]])))
		self.coordinate_velocities[0] = 1
		self.proper_velocities = list(symbols(" ".join(["w_" + i for i in [x0, x1, x2, x3]])))

	def __iter__(self):
		self._n = -1
		return self
	
	def __next__(self):
		self._n += 1 
		if self._n == 4:
			raise StopIteration
		return self.coordinates[self._n]

	def x(self, i: int) -> Symbol:
		"""
		Get the ith position coordinate (x^i).
		"""
		return self.coordinates[i]
	
	def dx(self, i: int) -> Symbol:
		"""
		Get the ith position differential element (dx^i).
		"""
		return self.differential_elements[i]

	def v(self, i: int) -> Symbol:
		"""
		Get the ith coordinate velocity component (dx^i/dt).
		"""
		return self.coordinate_velocities[i]

	def w(self, i: int) -> Symbol:
		"""
		Get the ith proper velocity component (dx^i/dtau).
		"""
		return self.proper_velocities[i]
	
	# Substitutions

	def coordinate_velocity_substitution(self, expr: Symbol, use0: bool=True, use1: bool=True, use2: bool=True, use3: bool=True):
		use = [use0, use1, use2, use3]
		for i, u in enumerate(use):
			if u:
				expr = expr.subs()

	# Implementations

	@classmethod
	def txyz(cls):
		"""
		The Cartesian coordinate system.
		"""
		return cls("t", "x", "y", "z")

	@classmethod
	def trtp(cls):
		"""
		The spherical coordinate system.
		"""
		return cls("t", "r", "theta", "phi")

	@classmethod
	def trtz(cls):
		"""
		The cylindrical coordinate system.
		"""
		return cls("t", "r", "theta", "z")

class MetricTensor:

	"""
	The MetricTensor class.

	Stores information about the metric tensor (g_ij),
	its inverse (g^ij), derivatives in all four directions
	of both tensors, and both determinants. The
	CoordinateSystem must be provided so that derivatives
	can be determined.
	"""

	coordinates: CoordinateSystem = None
	metric_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	metric_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	metric_determinant_uu = None
	metric_determinant_dd = None
	_is_diagonal = None

	def __init__(self, coords: CoordinateSystem, tensor: Matrix, indexing: str) -> None:
		self.coordinates = coords

		if (indexing == "uu"):
			self.metric_tensor_uu = Matrix(tensor)
			self.metric_tensor_dd = self.metric_tensor_uu.inv()
		elif indexing == "dd":
			self.metric_tensor_dd = Matrix(tensor)
			self.metric_tensor_uu = self.metric_tensor_dd.inv()

		self.metric_determinant_uu = self.metric_tensor_uu.det()
		self.metric_determinant_dd = self.metric_tensor_dd.det()

	def is_diagonal(self):
		if self.is_diagonal is None:
			d = None
			for i in range(4):
				for j in range(4):
					if i == j and 0 in (self.dd(i), self.uu(i)):
						d = False
						break
					elif i != j and (self.dd(i) != 0 or self.uu(i) != 0):
						d = False
						break
				if d is not None:
					break
			self._is_diagonal = d
		return self._is_diagonal

	def uu(self, i: int, j: int) -> Symbol:
		"""
		Component g^ij.
		"""
		return self.metric_tensor_uu[i, j]
	
	def dd(self, i: int, j: int) -> Symbol:
		"""
		Component g_ij.
		"""
		return self.metric_tensor_dd[i, j]

	def det_uu(self):
		"""
		The determinant of g^ij.
		"""
		return self.metric_determinant_uu

	def det_dd(self):
		"""
		The determinant of g_ij.
		"""
		return self.metric_determinant_dd

	# Examples

	@classmethod
	def minkowski_txyz(cls, units: UnitSystem):
		"""
		The Minkowski metric in Cartesian coordinates
		with a particular system of units.
		
		Metric from Gravitation.
		Christoffel symbols verified.
		Riemann tensor verified.
		Ricci tensor verified.
		Ricci scalar verified.
		Einstein tensor verified.
		SEM tensor verified
		"""
		return cls(CoordinateSystem.txyz(), [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]], "dd")

	@classmethod
	def minkowski_trtp(cls, units: UnitSystem):
		"""
		The Minkowski metric in spherical coordinates
		with a particular system of units.

		Metric from Gravitation.
		Christoffel symbols verified.
		Riemann tensor verified.
		Ricci tensor verified.
		Ricci scalar verified.
		Einstein tensor verified.
		SEM tensor verified.
		"""
		coords = CoordinateSystem.trtp()
		r2 = coords.x(1) ** 2
		theta = coords.x(2)
		return cls(coords, [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -r2, 0], [0, 0, 0, -r2 * sin(theta)**2]], "dd")
	
	@classmethod
	def schwarzschild_txyz(cls, units: UnitSystem):
		"""
		The Schwarzschild metric in Cartesian
		coordinates with a particular system of units.

		Not yet tested.
		"""
		coords = CoordinateSystem.txyz()
		M = Symbol("M")
		r = sqrt(coords.x(1)**2 + coords.x(2)**2 + coords.x(3)**2)
		r_s = Symbol("r_s")
		k = 1 - r_s/r
		return cls(coords, [[k * units.c**2, 0, 0, 0], [0, -1/k, 0, 0], [0, 0, -1/k, 0], [0, 0, 0, -1/k]], "dd")
	
	@classmethod
	def schwarzschild_trtp(cls, units: UnitSystem):
		"""
		The Schwarzschild metric in spherical
		coordinates with a particular system of units.

		Metric from Gravitation.
		Christoffel symbols verified.
		Riemann tensor verified.
		Ricci tensor verified.
		Ricci scalar verified.
		Einstein tensor verified.
		SEM tensor verified.
		"""
		coords = CoordinateSystem.trtp()
		r = coords.x(1)
		r2 = r ** 2
		theta = coords.x(2)
		M = Symbol("M")
		r_s = 2*units.G*M / (units.c**2)
		k = 1 - r_s/r
		return cls(coords, [[units.c**2 * k, 0, 0, 0], [0, -1/k, 0, 0], [0, 0, -r2, 0], [0, 0, 0, -r2 * sin(theta)**2]], "dd")

	@classmethod
	def alcubierre_txyz(cls, units=UnitSystem.si_ncc()):
		"""
		The Alcubierre warp drive in Cartesian
		coordinates.

		Not yet tested.
		"""
		coords = CoordinateSystem.txyz()
		v_s, r_s = Symbol("v_s"), sqrt(coords.x(1)**2 + coords.x(2)**2 + coords.x(3)**2)
		f = Function("f")(r_s)
		return cls(coords, [[units.c**2 - (v_s**2 * f**2), v_s*f/2, 0, 0], [v_s*f, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]], "dd")
	
	@classmethod
	def lvfd_txyz(cls, units=UnitSystem.si()):
		"""
		The lambdavacuum frame-dragging warp drive
		in Cartesian coordinates.
		
		Not yet tested.
		"""
		coords = CoordinateSystem.txyz()
		phi = Function("phi")(*coords.coordinates) # Function("phi")(coords.x(0), coords.x(1), coords.x(2), coords.x(3))
		return cls(coords, [[units.c**2, phi/2, 0, 0], [phi/2, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]], "dd")

	@classmethod
	def lvfd_trtz(cls, units=UnitSystem.si()):
		"""
		The lambdavacuum frame-dragging warp drive
		in alternative cylindrical coordinates.

		Not yet tested.
		"""
		coords = CoordinateSystem.trtz()
		phi = Function("phi")(coords.x(1), coords.x(3))
		r = coords.x(1)
		return cls(coords, [[units.c**2, phi/2, 0, 0], [phi/2, -1, 0, 0], [0, 0, -r**2, 0], [0, 0, 0, -1]], "dd")

class GeneralRankTwoTensor:

	"""
	The GeneralRankTwoTensor class. Describes a Rank-2 tensor.

	Comes with methods for element calculation and
	access, as well as other doodads.
	"""

	tensor_uu = [[None for i in range(4)] for j in range(4)]
	tensor_dd = [[None for i in range(4)] for j in range(4)]
	requisites = None
	metric_tensor = None
	symmetry = None

	def __init__(self, metric: MetricTensor, indexing: str=None, symmetry=None, *T, **requisites):
		self.metric_tensor = metric
		self.requisites = requisites
		if len(T) == 0:
			return
		elif len(T) != 4:
			raise IndexError("GeneralRankTwoTensor must be a 4D 2-form (i.e. 4x4).")
		if indexing == "uu":
			self.tensor_uu = T
		elif indexing == "dd":
			self.tensor_dd = T

		self.symmetry = symmetry

		if Configuration.autocompute:
			self.compute()

	def find_uu(i, j):
		if Configuration.autoindex:
			return self.raise_indices(i, j)
		return NotImplemented("GeneralRankTwoTensor's contravariant finder not implemented. Try Configuration.set_autoindex(True) to use index raising.")

	def find_dd(i, j):
		if Configuration.autoindex:
			return self.lower_indices(i, j)
		return NotImplemented("GeneralRankTwoTensor's covariant finder not implemented. Try Configuration.set_autoindex(True) to use index lowering.")

	def uu(self, i, j):
		if self.tensor_uu[i][j] is None:
			computation = self.find_uu(i, j)
			self.tensor_uu[i][j] = computation
			if self.symmetry == SYMMETRIC:
				self.tensor_uu[j][i] = computation
			if self.symmetry == ANTISYMMETRIC:
				self.tensor_uu[j][i] = -1 * computation
		return self.tensor_uu[i][j]

	def dd(self, i, j):
		if self.tensor_dd[i][j] is None:
			computation = self.find_dd(i, j)
			self.tensor_dd[i][j] = computation
			if self.symmetry == SYMMETRIC:
				self.tensor_dd[j][i] = computation
			if self.symmetry == ANTISYMMETRIC:
				self.tensor_dd[j][i] = -1 * computation
		return self.tensor_dd[i][j]

	def compute_uu(self):
		for i in range(4):
			for j in range(4):
				self.uu(i, j)

	def compute_dd(self):
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def compute(self):
		self.compute_uu()
		self.compute_dd()

	def raise_indices(self, i, j):
		"""
		Use index raising to find contravariant components (requires metric).
		"""
		if self.dd(i, j) is None:
			raise RuntimeError("Cannot raise indices on tensor as the lower-index component is None.")

		Tuu = 0
		for k in range(4):
			for l in range(4):
				Tuu = Tuu + (self.metric_tensor.uu(i, k) * self.metric_tensor.uu(j, l) * self.dd(k, l)) 
		return Tuu

	def lower_indices(self, i, j):
		"""
		Use index lowering to find covariant components (requires metric).
		"""
		if self.uu(i, j) is None:
			raise RuntimeError("Cannot raise indices on tensor as the lower-index component is None.")

		Tdd = 0
		for k in range(4):
			for l in range(4):
				Tdd = Tdd + (self.metric_tensor.dd(i, k) * self.metric_tensor.dd(j, l) * self.uu(k, l)) 
		return Tdd
	
	# Math operators

	def __add__(self, other: "GeneralRankTwoTensor") -> "GeneralRankTwoTensor":
		self.compute()
		other.compute()
		T = GeneralRankTwoTensor(self.metric, "dd")
		T.requisites.update(other.requisites)
		for i in range(4):
			for j in range(4):
				T.tensor_uu[i][j] = self.uu(i, j) + other.uu(i, j)
				T.tensor_dd[i][j] = self.dd(i, j) + other.dd(i, j)
		return T
	
	def __sub__(self, other: "GeneralRankTwoTensor") -> "GeneralRankTwoTensor":
		self.compute()
		other.compute()

		T = GeneralRankTwoTensor(self.metric, "dd")
		T.requisites.update(other.requisites)
		for i in range(4):
			for j in range(4):
				T.tensor_uu[i][j] = self.uu(i, j) - other.uu(i, j)
				T.tensor_dd[i][j] = self.dd(i, j) - other.dd(i, j)
		return T

class GeneralRankThreeTensor:

	"""
	The GeneralRankThreeTensor class. Describes a Rank-3 tensor.

	Comes with methods for element calculation and
	access, as well as other doodads.
	"""

	tensor_uuu = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	tensor_ddd = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	requisites = None
	metric_tensor = None
	symmetry = None

	def __init__(self, metric: MetricTensor, indexing: str=None, *T, **requisites):
		self.metric_tensor = metric
		self.requisites = requisites
		if len(T) == 0:
			return
		elif len(T) != 4:
			raise IndexError("GeneralRankThreeTensor must be a 4D 3-form (i.e. 4x4).")
		if indexing == "uuu":
			self.tensor_uuu = T
		elif indexing == "ddd":
			self.tensor_ddd = T
		else:
			raise IndexError("")

		self.symmetry = symmetry

		if Configuration.autocompute:
			self.compute()

	def find_uuu(i, j, k):
		if Configuration.autoindex:
			return self.raise_indices(i, j, k)
		return NotImplemented("GeneralTensor's contravariant finder not implemented. Try Configuration.set_autoindex(True) to use index raising.")

	def find_ddd(i, j, k):
		if Configuration.autoindex:
			return self.lower_indices(i, j, k)
		return NotImplemented("GeneralTensor's covariant finder not implemented. Try Configuration.set_autoindex(True) to use index lowering.")

	def uuu(self, i, j, k):
		if self.tensor_uuu[i][j][k] is None:
			computation = self.find_uu(i, j)
			self.tensor_uuu[i][j][k] = simplify(computation)
		return self.tensor_uuu[i][j][k]

	def dd(self, i, j):
		if self.tensor_dd[i][j][k] is None:
			computation = self.find_dd(i, j)
			self.tensor_dd[i][j][k] = simplify(computation)
		return self.tensor_dd[i][j][k]

	def compute_uuu(self):
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.uuu(i, j, k)

	def compute_ddd(self):
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.ddd(i, j, k)

	def compute(self):
		self.compute_uu()
		self.compute_dd()

	def raise_indices(self, i, j, k):
		"""
		Use index raising to find contravariant components (requires metric).
		"""
		if self.ddd(i, j, k) is None:
			raise RuntimeError("Cannot raise indices on tensor as the lower-index component is None.")

		Tuuu = 0
		for l in range(4):
			for m in range(4):
				for n in range(4):
					Tuu = Tuu + (self.metric_tensor.uu(i, l) * self.metric_tensor.uu(j, m) * self.metric_tensor.uu(k, n) * self.dd(l, m, n)) 
		return Tuuu

	def lower_indices(self, i, j):
		"""
		Use index lowering to find covariant components (requires metric).
		"""
		if self.uuu(i, j, k) is None:
			raise RuntimeError("Cannot lower indices on tensor as the upper-index component is None.")

		Tddd = 0
		for l in range(4):
			for m in range(4):
				for n in range(4):
					Tddd = Tddd + (self.metric_tensor.dd(i, l) * self.metric_tensor.dd(j, m) * self.metric_tensor.dd(k, n) * self.uu(l, m, n)) 
		return Tddd
	
	# Math operators

	def __add__(self, other: "GeneralTensor") -> "GeneralTensor":
		self.compute()
		other.compute()
		T = GeneralTensor(self.metric, "ddd")
		T.requisites.update(other.requisites)
		for i in range(4):
			for j in range(4):
				for k in range(4):
					T.tensor_uuu[i][j][k] = self.uuu(i, j, k) + other.uuu(i, j, k)
					T.tensor_ddd[i][j][k] = self.ddd(i, j, k) + other.ddd(i, j, k)
		return T
	
	def __sub__(self, other: "GeneralTensor") -> "GeneralTensor":
		self.compute()
		other.compute()
		T = GeneralTensor(self.metric, "ddd")
		T.requisites.update(other.requisites)
		for i in range(4):
			for j in range(4):
				for k in range(4):
					T.tensor_uuu[i][j][k] = self.uuu(i, j, k) - other.uuu(i, j, k)
					T.tensor_ddd[i][j][k] = self.ddd(i, j, k) - other.ddd(i, j, k)
		return T

GeneralTensor = Union[GeneralRankTwoTensor, GeneralRankThreeTensor]

class GeneralFourVector:

	update_alternate_indices = False
	vector_u = [None, None, None, None]
	vector_d = [None, None, None, None]
	metric_tensor = None
	coordinates: CoordinateSystem = None

	def __init__(self, metric: MetricTensor, indexing: str=None, *v):
		self.metric_tensor = metric
		self.coordinates = metric.coordinates
		if len(v) == 0:
			return
		elif len(v) != 4:
			raise IndexError("GeneralFourVectors are four-dimensional.")
		if indexing == "u":
			self.vector_u = v
		elif indexing == "d":
			self.vector_d = v

	def repr(self) -> str:
		return "<" + ", ".join(map(str, [self.u(i) for i in range(4)])) + ">"
	
	def __repr__(self) -> str:
		return self.repr()

	def find_u(self, i):
		raise NotImplemented("GeneralFourVector contravariant finder not implemented.")

	def find_d(self, i):
		raise NotImplemented("GeneralFourVector covariant finder not implemented.")

	def u(self, i):
		if self.vector_u[i] is None:
			if self.vector_d[i] is not None:
				component = 0
				for j in range(4):
					component = component + self.metric_tensor.uu(i, j)*self.d(j)
				self.vector_u[i] = component
			else:
				self.vector_u[i] = self.find_u(i)
		return self.vector_u[i]

	def d(self, i):
		if self.vector_d[i] is None:
			if self.vector_u[i] is not None:
				component = 0
				for j in range(4):
					component = component + self.metric_tensor.dd(i, j)*self.u(j)
				self.vector_d[i] = component
			else:
				self.vector_d[i] = self.find_d(i)
		return self.vector_d[i]

	def compute_u(self):
		for i in range(4):
			self.u(i)

	def compute_d(self):
		for i in range(4):
			self.d(i)

	def compute(self):
		self.compute_u()
		self.compute_d()

	def subs(self, a, b):
		self.compute()
		result = GeneralFourVector(self.metric_tensor, "u", 0, 0, 0, 0)
		for i in range(4):
			result.vector_d[i] = self.d(i).subs(a, b)
			result.vector_u[i] = self.u(i).subs(a, b)
		return result

	@classmethod 
	def zero(cls, metric: MetricTensor) -> "GeneralFourVector":
		return cls(metric, "dd", 0, 0, 0, 0)
	
	# Math

	def __add__(self, other: "GeneralFourVector") -> "GeneralFourVector":
		try:
			self.compute()
			other.compute()
		except NotImplemented:
			pass

		v = GeneralFourVector(self.metric_tensor)
		for i in range(4):
			v.vector_u[i] = self.u(i) + other.u(i)
			v.vector_d[i] = self.d(i) + other.d(i)
		return v

	def __sub__(self, other: "GeneralFourVector") -> "GeneralFourVector":
		try:
			self.compute()
			other.compute()
		except NotImplemented:
			pass

		v = GeneralFourVector(self.metric_tensor)
		for i in range(4):
			v.vector_u[i]  = self.u(i) - other.u(i)
			v.vector_d[i] = self.d(i) - other.d(i)
		return v

	def __mul__(self, scal: float) -> "GeneralFourVector":
		self.compute()
		v = GeneralFourVector(self.metric_tensor)
		for i in range(4):
			v.vector_u[i] = self.u(i) * scal
			v.vector_d[i] = self.d(i) * scal
		return v

	def __matmul__(self, other: "GeneralFourVector") -> Symbol:
		"""
		Return the square of the distance between the
		vectors according to the metric.

		The metric used is that of the LEFT operand.
		I'm not quite sure how to check if two metrics
		are equal yet, so...

		Returns the square so I don't have to deal 
		with imaginary values.
		"""
		self.compute()
		other.compute()
		dx = GeneralFourVector(
			self.metric_tensor, "u",
			other.u(0) - self.u(0),
			other.u(1) - self.u(1),
			other.u(2) - self.u(2),
			other.u(3) - self.u(3)
		)
		ds2 = 0
		for i in range(4):
			for j in range(4):
				ds2 = ds2 + (self.metric_tensor.dd(i, j) * dx.u(i) * dx.u(j))
		return ds2

	def norm(self):
		"""
		Return the norm of the vector according to 
		the metric.

		Returns the square so I don't have to deal
		with imaginary values.
		"""

		self.compute()
		ds2 = 0
		for i in range(4):
			for j in range(4):
				ds2 = ds2 + self.metric_tensor.dd(i, j) * self.u(i) * self.u(j)
		return ds2

# ===== EINSTEIN FIELD EQUATION COMPONENTS ===== #

class ChristoffelSymbols:

	"""
	The ChristoffelSymbols class.

	Stores and computes Christoffel symbols of the first
	and second kind, as well as their derivatives. Requires
	the MetricTensor to be provided so that the symbols
	can be computed.
	"""

	coordinates: CoordinateSystem = None
	metric_tensor: MetricTensor = None

	christoffel_symbols_udd = tensor.array.MutableDenseNDimArray(range(64), (4, 4, 4))
	_christoffel_symbols_udd_computed = [[[False for i in range(4)] for j in range(4)] for k in range(4)]
	christoffel_symbols_ddd = tensor.array.MutableDenseNDimArray(range(64), (4, 4, 4))
	_christoffel_symbols_ddd_computed = [[[False for i in range(4)] for j in range(4)] for k in range(4)]

	christoffel_symbols_udd_diff = tensor.array.MutableDenseNDimArray(range(256), (4, 4, 4, 4))
	_christoffel_symbols_udd_diff_computed = [[[[False for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]
	christoffel_symbols_ddd_diff = tensor.array.MutableDenseNDimArray(range(256), (4, 4, 4, 4))
	_christoffel_symbols_ddd_diff_computed = [[[[False for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, metric: MetricTensor) -> None:
		self.metric_tensor = metric
		self.coordinates = metric.coordinates

		if Configuration.autocompute:
			self.compute()

	def udd(self, i, k, l):
		"""
		The Christoffel symbol of the second kind: Gamma^i_kl.
		"""
		if not self._christoffel_symbols_udd_computed[i][k][l]:
			symbol = 0
			for m in range(4):
				symbol = symbol + Rational("1/2")*self.metric_tensor.uu(m,i)*(diff(self.metric_tensor.dd(l,m), self.coordinates.x(k))+diff(self.metric_tensor.dd(m,k), self.coordinates.x(l))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(m)))
			self.christoffel_symbols_udd[i,k,l] = simplify(symbol)
			self._christoffel_symbols_udd_computed[i][k][l] = True
			self.christoffel_symbols_udd[i,l,k] = self.christoffel_symbols_udd[i,k,l]
			self._christoffel_symbols_udd_computed[i][l][k] = True
		return self.christoffel_symbols_udd[i, k, l]

	def udd_diff(self, i, k, l, m):
		if not self._christoffel_symbols_udd_diff_computed[i][k][l][m]:
			self.christoffel_symbols_udd_diff[i, k, l, m] = self.udd(i, k, l).diff(self.coordinates.x(m))
			self._christoffel_symbols_udd_diff_computed[i][k][l][m] = True
		return self.christoffel_symbols_udd_diff[i, k, l, m]
	
	def ddd(self, i, k, l):
		"""
		The Christoffel symbol of the first kind: Gamma_ikl.
		"""
		if not self._christoffel_symbols_ddd_computed[i][k][l]:
			self.christoffel_symbols_ddd[i,k,l] = simplify(Rational('1/2')*(diff(self.metric_tensor.dd(i,k), self.coordinates.x(l))+diff(self.metric_tensor.dd(i,l), self.coordinates.x(k))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(i))))
			self._christoffel_symbols_ddd_computed[i][k][l] = True
		return self.christoffel_symbols_ddd[i, k, l]

	def ddd_diff(self, i, k, l, m):
		if not self._christoffel_symbols_ddd_diff_computed[i][k][l][m]:
			self.christoffel_symbols_ddd_diff[i, k, l, m] = self.ddd(i, k, l).diff(self.coordinates.x(m))
			self._christoffel_symbols_ddd_diff_computed[i][k][l][m] = True
		return self.christoffel_symbols_ddd_diff[i, k, l, m]

	def compute_udd(self):
		"""
		Compute all Christoffel symbols of the second kind.
		"""
		
		with ProgressBar("Computing Christoffel symbols of the second kind", 64) as pb:
			for i in range(4):
				for j in range(4):
					for k in range(4):
						self.udd(i, j, k)
						for l in range(4):
							self.udd_diff(i, j, k, l)
						pb.done()

	def compute_ddd(self):
		"""
		Compute all Christoffel symbols of the first kind.
		"""
				
		with ProgressBar("Computing Christoffel symbols of the first kind", 64) as pb:
			for i in range(4):
				for j in range(4):
					for k in range(4):
						self.ddd(i, j, k)
						for l in range(4):
							self.ddd_diff(i, j, k, l)
						pb.done()

	def compute(self):
		"""
		Compute all Christoffel symbols of both kinds.
		"""
		self.compute_udd()
		self.compute_ddd()

class RiemannTensor:

	"""
	The RiemannTensor class.

	Stores information about all-covariant and 
	contravariant-covariant (uddd) Riemann tensors.
	Requires a bit more complexity because SymPy
	doesn't like 4D arrays (but so do the
	ChristoffelSymbols). Requires the CoordinateSystem
	and the MetricTensor to take derivatives of the
	metric.
	"""

	coordinates: CoordinateSystem = None
	metric_tensor: MetricTensor = None
	christoffel_symbols: ChristoffelSymbols = None
	riemann_tensor_uddd = tensor.array.MutableDenseNDimArray(range(256), (4, 4, 4, 4))
	_riemann_tensor_uddd_computed = [[[[False for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]
	riemann_tensor_dddd = tensor.array.MutableDenseNDimArray(range(256), (4, 4, 4, 4))
	_riemann_tensor_dddd_computed = [[[[False for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, christoffel: ChristoffelSymbols) -> None:
		self.metric_tensor = christoffel.metric_tensor
		self.coordinates = self.metric_tensor.coordinates
		self.christoffel_symbols = christoffel

		if Configuration.autocompute:
			self.compute()

	def uddd(self, i, k, l, m):
		"""
		The Riemann tensor component R^r_smn.
		"""
		if not self._riemann_tensor_uddd_computed[i][k][l][m]:
			coefficient = 0
			if RIEMANN_UDDD_MODE == CHRISTOFFEL_SYMBOLS:
				coefficient = self.christoffel_symbols.udd_diff(i, m, k, l) - self.christoffel_symbols.udd_diff(i, l, k, m)
				for j in range(4):
					p1 = self.christoffel_symbols.udd(i, l, j) * self.christoffel_symbols.udd(j, m, k)
					p2 = self.christoffel_symbols.udd(i, m, j) * self.christoffel_symbols.udd(j, l, k)
					coefficient = coefficient + p1 - p2
					coefficient = simplify(coefficient)
			elif RIEMANN_UDDD_MODE == INDEX_RAISING:
				for j in range(4):
					coefficient = coefficient + self.metric_tensor.uu(j, rho)*self.dddd(j, k, l, m)
				coefficient = simplify(coefficient)
			self.riemann_tensor_uddd[i, k, l, m] = coefficient
			self._riemann_tensor_uddd_computed[i][k][l][m] = True
		return self.riemann_tensor_uddd[i, k, l, m]

	def dddd(self, i, k, l, m):
		"""
		The Riemann tensor component R_rsmn.
		"""
		if not self._riemann_tensor_dddd_computed[i][k][l][m]:
			xi, xk, xl, xm = self.coordinates.x(i), self.coordinates.x(k), self.coordinates.x(l), self.coordinates.x(m)
			coefficient = Rational("1/2")*(self.metric_tensor.dd(i, m).diff(xk, xl) + self.metric_tensor.dd(k, l).diff(xi, xm) - self.metric_tensor.dd(i, l).diff(xk, xm) - self.metric_tensor.dd(k, m).diff(xi, xl))
			# coefficient = simplify(coefficient)
			self.riemann_tensor_dddd[i, k, l, m] = simplify(coefficient)
			self._riemann_tensor_dddd_computed[i][k][l][m] = True
		return self.riemann_tensor_dddd[i, k, l, m]

	def compute_uddd(self):
		"""
		Compute all uddd components.
		"""
				
		with ProgressBar("Computing uddd Riemann tensor components", 256) as pb:
			for i in range(4):
				for j in range(4):
					for k in range(4):
						for l in range(4):
							self.uddd(i, j, k, l)
							pb.done()

	def compute_dddd(self):
		"""
		Compute all dddd components.
		"""
				
		with ProgressBar("Computing all-covariant Riemann tensor components", 256) as pb:
			for i in range(4):
				for j in range(4):
					for k in range(4):
						for l in range(4):
							self.dddd(i, j, k, l)
							pb.done()

	def compute(self):
		"""
		Compute all components.
		"""
		self.compute_uddd()
		self.compute_dddd()

class RicciTensor:

	"""
	The RicciTensor class.

	Stores information about the covariant, contravariant,
	and mixed Ricci tensors, as well as the Ricci scalar.
	Must be supplied with the RiemannTensor (I'm working
	on a way to allow it to alternatively use the
	ChristoffelSymbols instead but this is what I have for
	now) to calculate the Ricci tensor. The MetricTensor
	is obtained from the RiemannTensor object passed in.
	"""

	metric_tensor: MetricTensor = None
	riemann_tensor: RiemannTensor = None
	ricci_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	ricci_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	ricci_tensor_ud = Matrix([[None for i in range(4)] for j in range(4)])
	ricci_scalar = None

	def __init__(self, riemann: RiemannTensor) -> None:
		self.riemann_tensor = riemann
		self.metric_tensor = self.riemann_tensor.metric_tensor

		if Configuration.autocompute:
			self.compute()

	def dd(self, mu: int, nu: int) -> Symbol:
		"""
		The Ricci tensor component R_mn.
		"""
		if self.ricci_tensor_dd[mu, nu] is None:
			coefficient = 0
			for lam in range(4):
				coefficient = coefficient + self.riemann_tensor.uddd(lam, mu, lam, nu)
			self.ricci_tensor_dd[mu, nu] = simplify(coefficient)
			self.ricci_tensor_dd[nu, mu] = self.ricci_tensor_dd[mu, nu]
		return self.ricci_tensor_dd[mu,nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		"""
		The Ricci tensor component R^mn.
		"""
		if self.ricci_tensor_uu[mu, nu] is None:
			coefficient = 0
			for rho in range(4):
				for sig in range(4):
					coefficient = coefficient + self.metric_tensor.uu(mu, rho)*self.metric_tensor.uu(nu, sig)*self.dd(rho, sig)
			self.ricci_tensor_uu[mu, nu] = simplify(coefficient)
			self.ricci_tensor_uu[nu, mu] = self.ricci_tensor_uu[mu, nu]
		return self.ricci_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		"""
		The Ricci tensor component R^m_n.
		"""
		raise RuntimeError("The developer needs to fix the RicciTensor.ud method which was never implemented.")

	def scalar(self) -> Symbol:
		"""
		The Ricci scalar.
		"""
		if self.ricci_scalar is None:
			scalar = 0
			for mu in range(4):
				for nu in range(4):
					scalar = scalar + self.metric_tensor.uu(mu, nu) * self.dd(mu, nu)
			self.ricci_scalar = simplify(scalar)
		return self.ricci_scalar

	def compute_dd(self):
		"""
		Compute all covariant components.
		"""
				
		with ProgressBar("Computing covariant Ricci tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.dd(i, j)
					pb.done()

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
				
		with ProgressBar("Computing contravariant Ricci tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.uu(i, j)
					pb.done()

	def compute_scalar(self):
		"""
		Compute the Ricci scalar.
		"""
		self.scalar()

	def compute(self):
		"""
		Compute everything.
		"""
		self.compute_dd()
		self.compute_uu()
		self.compute_scalar()

class WeylTensor:

	"""
	The WeylTensor class.

	Stores information about all-covariant Weyl
	tensors. Requires the Ricci tensor (whence
	it can obtain the Riemann and metric tensors).
	"""

	metric_tensor: MetricTensor = None
	riemann_tensor: RiemannTensor = None
	ricci_tensor: RicciTensor = None
	weyl_tensor_dddd = tensor.array.MutableDenseNDimArray(range(256), (4, 4, 4, 4))
	_weyl_tensor_dddd_computed = [[[[False for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, ricci: RicciTensor) -> None:
		self.metric_tensor = ricci.metric_tensor
		self.riemann_tensor = ricci.riemann_tensor
		self.ricci_tensor = ricci

		if Configuration.autocompute:
			self.compute()

	def dddd(self, i, k, l, m):
		"""
		The Weyl tensor component C_iklm.
		"""
		if not self._weyl_tensor_dddd_computed[i][k][l][m]:
			coeff = self.riemann_tensor.dddd(i, k, l, m) + (Rational("1/2")*(
				self.ricci_tensor.dd(i, m)*self.metric_tensor.dd(k, l) - self.ricci_tensor.dd(i, l)*self.metric_tensor.dd(k, m) \
				+ self.ricci_tensor.dd(k, l)*self.metric_tensor.dd(i, m) - self.ricci_tensor.dd(k, m)*self.metric_tensor.dd(i, l)
			)) + (Rational("1/6")*self.ricci_tensor.scalar()*(self.metric_tensor.dd(i, l)*self.metric_tensor.dd(k, m) - self.metric_tensor.dd(i, m)*self.metric_tensor.dd(k, l)))
			self.weyl_tensor_dddd[i, k, l, m] = coeff
			self._weyl_tensor_dddd_computed[i][k][l][m] = True
			self.weyl_tensor_dddd[k, i, l, m] = -coeff
			self._weyl_tensor_dddd_computed[k][i][l][m] = True
			self.weyl_tensor_dddd[i, k, m, l] = -coeff
			self._weyl_tensor_dddd_computed[i][k][m][l] = True
		return self.weyl_tensor_dddd[i, k, l, m]

	def compute_dddd(self):
		"""
		Compute all dddd components.
		"""
				
		with ProgressBar("Computing all-covariant Weyl tensor components", 256) as pb:
			for i in range(4):
				for j in range(4):
					for k in range(4):
						for l in range(4):
							self.dddd(i, j, k, l)
							pb.done()

	def compute(self):
		"""
		Compute all components.
		"""
		self.compute_dddd()

class EinsteinTensor:

	"""
	The EinsteinTensor class.

	Stores information about the Einstein tensor. Requires
	the RicciTensor to calculate everything. The MetricTensor
	is had from the RicciTensor object that's passed in.
	"""

	metric_tensor: MetricTensor = None
	ricci_tensor: RicciTensor = None
	einstein_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	einstein_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	einstein_tensor_ud = Matrix([[None for i in range(4)] for j in range(4)])

	def __init__(self, ricci: RicciTensor) -> None:
		self.ricci_tensor = ricci
		self.metric_tensor = self.ricci_tensor.metric_tensor

		if Configuration.autocompute:
			self.compute()

	def dd(self, mu, nu):
		"""
		The Einstein tensor component G_mn.
		"""
		if self.einstein_tensor_dd[mu, nu] is None:
			self.einstein_tensor_dd[mu, nu] = simplify(self.ricci_tensor.dd(mu, nu) - Rational("1/2")*self.ricci_tensor.scalar()*self.metric_tensor.dd(mu, nu))
			self.einstein_tensor_dd[nu, mu] = self.einstein_tensor_dd[mu, nu]
		return self.einstein_tensor_dd[mu, nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		"""
		The Einstein tensor component G^mn.
		"""
		if self.einstein_tensor_uu[mu, nu] is None:
			self.einstein_tensor_uu[mu, nu] = simplify(self.ricci_tensor.uu(mu, nu) - Rational("1/2")*self.ricci_tensor.scalar()*self.metric_tensor.uu(mu, nu))
			self.einstein_tensor_uu[nu, mu] = self.einstein_tensor_uu[mu, nu]
		return self.einstein_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		"""
		The Einstein tensor component G^m_n.
		"""
		raise RuntimeError("The developer needs to fix the EinsteinTensor.ud method which was never implemented.")

	def compute_dd(self):
		"""
		Compute all covariant components.
		"""
				
		with ProgressBar("Computing covariant Einstein tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.dd(i, j)
					pb.done()

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
				
		with ProgressBar("Computing contravariant Einstein tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.uu(i, j)
					pb.done()

	def compute(self):
		"""
		Compute all components.
		"""
		self.compute_dd()
		self.compute_uu()

class SchoutenTensor:

	"""
	The SchoutenTensor class.

	Stores information about the Schouten tensor. Requires
	the RicciTensor to calculate everything. The MetricTensor
	is had from the RicciTensor object that's passed in.
	"""

	metric_tensor: MetricTensor = None
	ricci_tensor: RicciTensor = None
	schouten_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	schouten_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	einstein_tensor_ud = Matrix([[None for i in range(4)] for j in range(4)])

	def __init__(self, ricci: RicciTensor) -> None:
		self.ricci_tensor = ricci
		self.metric_tensor = self.ricci_tensor.metric_tensor

		if Configuration.autocompute:
			self.compute()

	def dd(self, mu, nu):
		"""
		The Schouten tensor component P_mn.
		"""
		if self.schouten_tensor_dd[mu, nu] is None:
			self.schouten_tensor_dd[mu, nu] = simplify(Rational("1/2")*(self.ricci_tensor.dd(mu, nu) - self.ricci_tensor.scalar()*self.metric_tensor.dd(mu, nu)/6))
			self.schouten_tensor_dd[nu, mu] = self.schouten_tensor_dd[mu, nu]
		return self.schouten_tensor_dd[mu, nu]

	def uu(self, mu, nu):
		"""
		The Schouten tensor component P_mn.
		"""
		if self.schouten_tensor_uu[mu, nu] is None:
			self.schouten_tensor_uu[mu, nu] = simplify(Rational("1/2")*(self.ricci_tensor.uu(mu, nu) - self.ricci_tensor.scalar()*self.metric_tensor.uu(mu, nu)/6))
			self.schouten_tensor_uu[nu, mu] = self.schouten_tensor_uu[mu, nu]
		return self.schouten_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		"""
		The Schouten tensor component P^m_n.
		"""
		raise RuntimeError("The developer needs to fix the EinsteinTensor.ud method which was never implemented.")

	def compute_dd(self):
		"""
		Compute all covariant components.
		"""
				
		with ProgressBar("Computing covariant Schouten tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.dd(i, j)
					pb.done()

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
				
		with ProgressBar("Computing contravariant Schouten tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.uu(i, j)
					pb.done()

	def compute(self):
		"""
		Compute all components.
		"""
		self.compute_dd()
		self.compute_uu()

class StressEnergyMomentumTensor:

	"""
	The stress-energy-momentum tensor - the object of
	the Einstein Field Equations - stored in the 
	StressEnergyMomentumTensor object.

	Stores the SEM tensor. Requires the Einstein tensor
	and a system of units (for Einstein's gravitational
	constant).
	"""

	units: UnitSystem = None
	metric_tensor: MetricTensor = None
	einstein_tensor: EinsteinTensor = None

	stress_energy_momentum_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	stress_energy_momentum_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	stress_energy_momentum_tensor_ud = Matrix([[None for i in range(4)] for j in range(4)])

	def __init__(self, einstein: EinsteinTensor, units: UnitSystem) -> None:
		self.units = units
		self.metric_tensor = einstein.metric_tensor
		self.einstein_tensor = einstein

		if Configuration.autocompute:
			self.compute()

	def dd(self, mu, nu):
		"""
		The SEM component T_mn.
		"""
		if self.stress_energy_momentum_tensor_dd[mu, nu] is None:
			self.stress_energy_momentum_tensor_dd[mu, nu] = simplify((self.einstein_tensor.dd(mu, nu) + self.units.Lambda*self.metric_tensor.dd(mu, nu)) / self.units.kappa)
			self.stress_energy_momentum_tensor_dd[nu, mu] = self.stress_energy_momentum_tensor_dd[mu, nu]
		return self.stress_energy_momentum_tensor_dd[mu, nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		"""
		The SEM component T^mn.
		"""
		if self.stress_energy_momentum_tensor_uu[mu, nu] is None:
			self.stress_energy_momentum_tensor_uu[mu, nu] = simplify((self.einstein_tensor.uu(mu, nu) + self.units.Lambda*self.metric_tensor.uu(mu, nu)) / self.units.kappa)
			self.stress_energy_momentum_tensor_uu[nu, mu] = self.stress_energy_momentum_tensor_uu[mu, nu]
		return self.stress_energy_momentum_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		"""
		The SEM component T^m_n.
		"""
		raise RuntimeError("The developer needs to fix the StressEnergyMomentumTensor.ud method which was never implemented.")

	def compute_dd(self):
		"""
		Compute all covariant components.
		"""
				
		with ProgressBar("Computing covariant SEM tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.dd(i, j)
					pb.done()

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
				
		with ProgressBar("Computing contravariant SEM tensor components", 16) as pb:
			for i in range(4):
				for j in range(4):
					self.uu(i, j)
					pb.done()

	def compute(self):
		"""
		Compute all components.
		"""
		self.compute_dd()
		self.compute_uu()

class GeodesicAccelerationVectors:

	units: UnitSystem = None
	coordinates: CoordinateSystem = None
	metric_tensor: MetricTensor = None
	christoffel_symbols: ChristoffelSymbols = None
	proper_geodesic_acceleration_vector = [None, None, None, None]
	proper_geodesic_acceleration_vector_gfv = None
	coordinate_geodesic_acceleration_vector = [None, None, None, None]
	coordinate_geodesic_acceleration_vector_gfv = None

	def __init__(self, christoffel: ChristoffelSymbols, units: UnitSystem=None) -> None:
		self.christoffel_symbols = christoffel
		self.coordinates = christoffel.coordinates
		self.units = units
		self.metric = christoffel.metric_tensor

		if Configuration.autocompute:
			self.compute()

	def proper(self, i: int) -> Symbol:
		"""
		ith component of proper acceleration,
		dx^i/dtau.
		"""
		if self.proper_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel_symbols.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.proper_geodesic_acceleration_vector[i] = accel
		return self.proper_geodesic_acceleration_vector[i]

	def proper_vector(self) -> GeneralFourVector:
		"""
		The full proper acceleration vector.
		"""
		if self.proper_geodesic_acceleration_vector_gfv is None:
			self.proper_geodesic_acceleration_vector_gfv = GeneralFourVector(
				self.metric_tensor, "u", 
				self.proper(0), self.proper(1), self.proper(2), self.proper(3)
			)
		return self.proper_geodesic_acceleration_vector_gfv

	def coordinate(self, i: int) -> Symbol:
		"""
		ith component of coordinate acceleration,
		dx^i/dt.
		
		Doesn't make much sense for i=0=t. dt/dt=1?
		"""
		if self.coordinate_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel_symbols.udd(0, mu, nu)*self.coordinates.v(i)*self.coordinates.v(mu)*self.coordinates.v(nu) - self.christoffel_symbols.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.coordinate_geodesic_acceleration_vector[i] = accel
		return self.coordinate_geodesic_acceleration_vector[i]

	def coordinate_vector(self) -> GeneralFourVector:
		"""
		The full coordinate acceleration vector.
		"""
		if self.coordinate_geodesic_acceleration_vector_gfv is None:
			self.coordinate_geodesic_acceleration_vector_gfv = GeneralFourVector(
				self.metric_tensor, "u", 
				self.coordinate(0), self.coordinate(1), 
				self.coordinate(2), self.coordinate(3)
			)
		return self.coordinate_geodesic_acceleration_vector_gfv
	
	def compute_proper(self):
		for i in range(4):
			self.proper(i)

	def compute_coordinate(self):
		for i in range(4):
			self.coordinate(i)

	def compute(self):
		self.compute_proper()
		self.compute_coordinate()

# ===== THE SPACETIME ===== #

class Spacetime:

	"""
	The Spacetime class.

	Stores all pertinent information about the spacetime.
	Put in a metric and system of units, and all other 
	relevant tensors are generated (evaluated lazily).
	"""

	units: UnitSystem = None
	coordinates: CoordinateSystem = None
	metric_tensor: MetricTensor = None
	christoffel_symbols: ChristoffelSymbols = None
	riemann_tensor: RiemannTensor = None
	ricci_tensor: RicciTensor = None
	weyl_tensor: WeylTensor = None
	schouten_tensor: SchoutenTensor = None
	einstein_tensor: EinsteinTensor = None
	stress_energy_momentum_tensor: StressEnergyMomentumTensor = None
	geodesic_acceleration_vectors: GeodesicAccelerationVectors = None
	parameterization: dict[str] = None

	# Run at object creation.
	def __init__(self, metric: MetricTensor, units: UnitSystem, **parameterization) -> None:
		self.units = units
		self.metric_tensor = metric
		self.coordinates = metric.coordinates
		
		self.christoffel_symbols = ChristoffelSymbols(self.metric_tensor)
		self.riemann_tensor = RiemannTensor(self.christoffel_symbols)
		self.ricci_tensor = RicciTensor(self.riemann_tensor)
		self.weyl_tensor = WeylTensor(self.ricci_tensor)
		self.schouten_tensor = SchoutenTensor(self.ricci_tensor)
		self.einstein_tensor = EinsteinTensor(self.ricci_tensor)
		self.stress_energy_momentum_tensor = StressEnergyMomentumTensor(self.einstein_tensor, self.units)
		self.geodesic_acceleration_vectors = GeodesicAccelerationVectors(self.christoffel_symbols, self.units)

		self.parameterization = parameterization

	def solve(self):
		"""
		Solve all the available tensors, vectors, etc.
		to obtain all information that we can about
		the spacetime.

		Adds a nice little display, too!
		"""

		print("Solving Einstein field equations & obtaining relevant spacetime information ...")
		st = time.time()
		ProgressBar.indent = 1
		self.christoffel_symbols.compute()
		self.riemann_tensor.compute()
		self.ricci_tensor.compute()
		self.weyl_tensor.compute()
		self.schouten_tensor.compute()
		self.einstein_tensor.compute()
		self.stress_energy_momentum_tensor.compute()
		self.geodesic_acceleration_vectors.compute()
		et = time.time()
		dt = et - st
		ProgressBar.indent = 0
		print("Solution complete, ancillary data found. Total elapsed computation time: " + str(repr_time(dt)))

	def compute(self):
		"""
		To be consistent about naming, since all the
		tensors and everything have .compute() as a
		method.
		"""
		self.solve()

	def _get_parameterization(self, p):
		result = self.parameterization
		for k in p.keys():
			result[k] = p[k]
		return result

	def parameterize(self, expr, point: GeneralFourVector, **kwargs):
		"""
		Give the value of the expression at a particular point 
		in spacetime given an arbitrary parameterization.

		Here, "parameterization" is a map from variables or
		parameters of the spacetime (like M, a, Q, v_s) to their
		chosen numerical values.
		"""

		parameterization = self._get_parameterization(kwargs)

		# Substitute coordinate values (i.e. x^1 -> 150 km)
		for i, coordinate in enumerate(self.coordinates):
			expr = expr.subs(coordinate, point.u(i))

		# Substitute parameterization (i.e. M -> 2e+30)
		for key in parameterization.keys():
			expr = expr.subs(Symbol(key), parameterization[key])
		
		# Substitute constants, or at least those not 
		# normalized by the unit system
		expr = expr.subs(Symbol("c"), REAL_c)
		expr = expr.subs(Symbol("G"), REAL_G)
		expr = expr.subs(Symbol("h"), REAL_h)
		expr = expr.subs(Symbol("Lambda"), REAL_Lambda)

		# Simplify
		expr = simplify(expr)

		return expr

	def evaluate(self, expr, point, **kwargs):
		"""
		Return a NUMERICAL VALUE SPECIFICALLY, as opposed
		to .parameterize() which doesn't necessarily.
		"""
		value = self.parameterize(expr, point, **kwargs)
		underdetermined = False
		try:
			value = float(value)
		except TypeError:
			underdetermined = True

		if underdetermined:
			s = "Insufficient parameterization to evaluate expression (underdetermined); symbols remaining: " + ", ".join(map(str, list(value.free_symbols)))
			raise UnderdeterminationError(s)
		return value