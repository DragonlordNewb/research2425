from sympy import *
from warnings import *
from abc import abstractmethod

simplefilter("ignore")

UU = "uu"
DD = "dd"

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
	proper_time = Symbol("tau")
	coordinate_velocities: list[Symbol] = None
	proper_velocities: list[Symbol] = None

	def __init__(self, x0, x1, x2, x3) -> None:
		self.coordinates = symbols(" ".join([x0, x1, x2, x3]))
		self.coordinate_velocities = [Derivative(self.x(i), self.x(0)) for i in range(4)]
		self.proper_velocities = [Derivative(self.x(i), self.proper_time) for i in range(4)]

	def x(self, i: int) -> Symbol:
		"""
		Get the ith position coordinate (dx^i).
		"""
		return self.coordinates[i]

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
	singularities = [None for i in range(4)]
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

	def locate_singularities(self, i: int):
		"""
		Determines if singularities exist.
		Returns whether or not there are any after
		putting the singularity conditions in the
		MetricTensor.singularities variable.

		Singularities occur where the metric determinant
		is zero (or where the metric is otherwise
		pathological for the given coordinate
		system). Using SymPy's algebraic solvers,
		we find those points for each coordinate
		to determine where the singular surfaces
		are.
		"""

		if self.is_diagonal():
			"""
			In a diagonal metric, there is a certain
			type of pathology when the metric components
			go to zero. For example, the Schwarzschild
			surface, which doesn't necessarily constitute
			a "singularity" but is certainly bad enough
			that an observer shouldn't try and cross it
			for our purposes.

			Find all the zeros of the metric components
			if they exist.
			"""

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
		Riemann tensor not verified.
		Ricci tensor not verified.
		Ricci scalar not verified.
		Einstein tensor not verified.
		SEM tensor not verified.
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

class GeneralTensor:

	"""
	The Rank2Tensor class. Describes a Rank-2 tensor.

	Comes with methods for element calculation and
	access, as well as other doodads.
	"""

	tensor_uu = [[None for i in range(4)] for j in range(4)]
	tensor_dd = [[None for i in range(4)] for j in range(4)]
	requisites = None
	metric = None

	def __init__(self, metric: MetricTensor, indexing: str, *T, **requisites):
		self.metric = metric
		self.requisites = requisites
		if len(rows) == 0:
			return
		elif len(rows) != 4:
			raise IndexError("GeneralTensor must be a 4D 2-form (i.e. 4x4).")
		if indexing == "uu":
			self.tensor_uu = T
		elif indexing == "dd":
			self.tensor_dd = T

	def find_uu(i, j):
		return NotImplemented("GeneralTensor's contravariant finder not implemented.")

	def find_dd(i, j):
		return NotImplemented("GeneralTensor covariant finder not implemented.")

	def uu(self, i, j):
		if self.tensor_uu[i][j] is None:
			computation = self.find_uu(i, j)
			self.tensor_uu[i][j] = computation
			self.tensor_uu[j][i] = computation
		return self.tensor_uu[i][j]

	def dd(self, i, j):
		if self.tensor_dd[i][j] is None:
			computation = self.find_dd(i, j)
			self.tensor_dd[i][j] = computation
			self.tensor_dd[j][i] = computation
		return self.tensor_dd[i][j]

	def compute_uu(self):
		for i in range(4):
			for j in range(4):
				self.uu(i, j)

	def compute_dd(self):
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def raise_indices(self, i, j):
		"""
		Use index raising to find contravariant components (requires metric).
		"""
		return

	def lower_indices(self, i, j):
		"""
		Use index lowering to find covariant components (requires metric).
		"""
		return

class GeneralFourVector:

	update_alternate_indices = False
	vector_u = [None, None, None, None]
	vector_d = [None, None, None, None]
	metric = None

	def __init__(self, metric: MetricTensor, indexing: str, *v):
		self.metric = metric
		if len(v) == 0:
			return
		elif len(v) != 4:
			raise IndexError("GeneralFourVectors are four-dimensional.")
		if indexing == "u":
			self.vector_u = v
		elif indexing == "d":
			self.vector_d = v

	def find_u(self, i):
		raise NotImplemented("GeneralFourVector contravariant finder not implemented.")

	def find_d(self, i):
		raise NotImplemented("GeneralFourVector covariant finder not implemented.")

	def u(self, i):
		if self.vector_u[i] is None:
			self.vector_u[i] = self.find_u(i)
		return self.vector_u[i]

	def d(self, i):
		if self.vector_d[i] is None:
			self.vector_d[i] = self.find_d(i)
		return self.vector_d[i]

	def compute_u(self):
		for i in range(4):
			self.u(i)

	def compute_d(self):
		for i in range(4):
			self.d(i)

	def raise_index(self, i):
		"""
		Use index raising to find contravariant components.
		"""
		return

	def lower_index(self, i):
		"""
		Use index lowering to find covariant components.
		"""
		return

	@classmethod 
	def zero(cls, metric: MetricTensor) -> GeneralFourVector:
		return cls(metric, "dd", 0, 0, 0, 0)

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

	def __init__(self, metric: MetricTensor) -> None:
		self.metric_tensor = metric
		self.coordinates = metric.coordinates

	def udd(self, i, k, l):
		"""
		The Christoffel symbol of the second kind: Gamma^i_kl.
		"""
		if not self._christoffel_symbols_udd_computed[i][k][l]:
			symbol = 0
			for m in range(4):
				symbol = symbol + Rational("1/2")*self.metric_tensor.uu(m,i)*(diff(self.metric_tensor.dd(k,m), self.coordinates.x(i))+diff(self.metric_tensor.dd(l,m), self.coordinates.x(k))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(m)))
			self.christoffel_symbols_udd[i,k,l] = simplify(symbol)
			self._christoffel_symbols_udd_computed[i][k][l] = True
			self.christoffel_symbols_udd[i,l,k] = self.christoffel_symbols_udd[i,k,l]
			self._christoffel_symbols_udd_computed[i][l][k] = True
		return self.christoffel_symbols_udd[i, k, l]
	
	def ddd(self, i, k, l):
		"""
		The Christoffel symbol of the first kind: Gamma_ikl.
		"""
		if not self._christoffel_symbols_ddd_computed[i][k][l]:
			self.christoffel_symbols_ddd[i,k,l] = simplify(Rational('1/2')*(diff(self.metric_tensor.dd(i,k), self.coordinates.x(l))+diff(self.metric_tensor.dd(i,l), self.coordinates.x(k))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(i))))
			self._christoffel_symbols_ddd_computed[i][k][l] = True
		return self.christoffel_symbols_ddd[i, k, l]

	def compute_udd(self):
		"""
		Compute all Christoffel symbols of the second kind.
		"""
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.udd(i, j, k)

	def compute_ddd(self):
		"""
		Compute all Christoffel symbols of the first kind.
		"""
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.ddd(i, j, k)

	def compute(self):
		"""
		Compute all Christoffel symbols of both kinds.
		"""
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.udd(i, j, k)
					self.ddd(i, j, k)

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

	def uddd(self, rho, sig, mu, nu):
		"""
		The Riemann tensor component R^r_smn.
		"""
		if not self._riemann_tensor_uddd_computed[rho][sig][mu][nu]:
			coefficient = diff(self.christoffel_symbols.udd(rho, nu, sig), self.coordinates.x(mu)) - diff(self.christoffel_symbols.udd(rho, mu, sig), self.coordinates.x(nu))
			for lam in self.coordinates.dimensions:
				coefficient = coefficient + self.christoffel_symbols.udd(rho, mu, lam)*self.christoffel_symbols.udd(lam, nu, sig) - self.christoffel_symbols.udd(rho, nu, lam)*self.christoffel_symbols.udd(lam, mu, sig)
			self.riemann_tensor_uddd[rho, sig, mu, nu] = simplify(coefficient)
			self._riemann_tensor_uddd_computed[rho][sig][mu][nu] = True
			self.riemann_tensor_uddd[mu, nu, rho, sig] = self.riemann_tensor_uddd[rho, sig, mu, nu]
			self._riemann_tensor_uddd_computed[rho][sig][mu][nu] = True
		return self.riemann_tensor_uddd[rho, sig, mu, nu]

	def dddd(self, rho, sig, mu, nu):
		"""
		The Riemann tensor component R_rsmn.
		"""
		if not self._riemann_tensor_dddd_computed[rho][sig][mu][nu]:
			coefficient = Rational('1/2')*(self.metric_tensor.dd(rho, nu).diff(self.coordinates.x(sig)).diff(self.coordinates(mu)) + self.metric_tensor.dd(sig, mu).diff(self.coordinates.x(rho)).diff(self.coordinates.x(nu))\
			-self.metric_tensor.dd(rho, mu).diff(self.coordinates.x(sig)).diff(self.coordinates.x(nu))-self.metric_tensor.dd(sig, nu).diff(self.coordinates.x(rho)).diff(self.coordinates.x(mu)))
			for n in range(4):
				for p in range(4):
					coefficient = coefficient + self.metric_tensor.dd(n, p)*(self.christoffel_symbols.udd(n, sig, mu)*self.christoffel_symbols.udd(p, rho, nu)-self.christoffel_symbols(n, sig, nu)*self.christoffel_symbols.udd(p, rho, mu))
			self.riemann_tensor_dddd[rho, sig, mu, nu] = simplify(coefficient)
			self._riemann_tensor_dddd_computed[rho][sig][mu][nu] = True
		return self.riemann_tensor_dddd[rho, sig, mu, nu]

	def compute_uddd(self):
		"""
		Compute all uddd components.
		"""
		for i in range(4):
			for j in range(4):
				for k in range(4):
					for l in range(4):
						self.uddd(i, j, k, l)

	def compute_dddd(self):
		"""
		Compute all dddd components.
		"""
		for i in range(4):
			for j in range(4):
				for k in range(4):
					for l in range(4):
						self.uddd(i, j, k, l)

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
			self.ricci_tensor_uu[nu, mu] = self.ricci_tensor_uu[nu, mu]
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
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
		for i in range(4):
			for j in range(4):
				self.uu(i, j)

	def compute_scalar(self):
		"""
		Compute the Ricci scalar.
		"""
		self.scalar()

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
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
		for i in range(4):
			for j in range(4):
				self.uu(i, j)

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
			self.stress_energy_momentum_tensor_uu[nu, mu] = self.stress_energy_momentum_tensor_uu[mu. nu]
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
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def compute_uu(self):
		"""
		Compute all contravariant components.
		"""
		for i in range(4):
			for j in range(4):
				self.uu(i, j)

class GeodesicAccelerationVectors:

	coordinates: CoordinateSystem = None
	christoffel_symbols: ChristoffelSymbols = None
	proper_geodesic_acceleration_vector = [None, None, None, None]
	coordinate_geodesic_acceleration_vector = [None, None, None, None]

	def __init__(self, christoffel: ChristoffelSymbols) -> None:
		self.christoffel_symbols = christoffel
		self.coordinates = christoffel.coordinates

	def proper(self, i: int) -> Symbol:
		if self.proper_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel_symbols.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.proper_geodesic_acceleration_vector[i] = accel
		return self.proper_geodesic_acceleration_vector[i]

	def coordinate(self, i: int) -> Symbol:
		if self.proper_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel_symbols.udd(0, mu, nu)*self.coordinates.v(i)*self.coordinates.v(mu)*self.coordinates.v(nu) - self.christoffel_symbols.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.proper_geodesic_acceleration_vector[i] = accel
		return self.proper_geodesic_acceleration_vector[i]
	
	def compute_proper(self):
		for i in range(4):
			self.proper(i)

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
	einstein_tensor: EinsteinTensor = None
	stress_energy_momentum_tensor: StressEnergyMomentumTensor = None
	geodesic_acceleration_vectors: GeodesicAccelerationVectors = None

	# Run at object creation.
	def __init__(self, metric: MetricTensor, units: UnitSystem) -> None:
		self.units = units
		self.metric_tensor = metric
		self.coordinates = metric.coordinates
		
		self.christoffel_symbols = ChristoffelSymbols(self.metric_tensor)
		self.riemann_tensor = RiemannTensor(self.christoffel_symbols)
		self.ricci_tensor = RicciTensor(self.riemann_tensor)
		self.einstein_tensor = EinsteinTensor(self.ricci_tensor)
		self.stress_energy_momentum_tensor = StressEnergyMomentumTensor(self.einstein_tensor, self.units)
		self.geodesic_acceleration_vectors = GeodesicAccelerationVectors(self.christoffel_symbols)