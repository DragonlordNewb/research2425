from sympy import *
from warnings import *

simplefilter("ignore")

UU = "uu"
DD = "dd"

class UnitSystem:

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
		return cls(False, False, False, False)
	
	@classmethod
	def si_ncc(cls):
		return cls(False, False, False, True)

	@classmethod
	def natural(cls):
		return cls(True, True, True, False)

	@classmethod
	def natural_ncc(cls):
		return cls(True, True, True, True)

class CoordinateSystem:

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
		return self.coordinates[i]

	def v(self, i: int) -> Symbol:
		return self.coordinate_velocities[i]

	def w(self, i: int) -> Symbol:
		return self.proper_velocities[i]

	# Implementations

	@classmethod
	def txyz(cls):
		return cls("t", "x", "y", "z")

	@classmethod
	def trtp(cls):
		return cls("t", "r", "theta", "phi")

	@classmethod
	def trtz(cls):
		return cls("t", "r", "theta", "z")


class MetricTensor:

	coordinates: CoordinateSystem = None
	metric_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	metric_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	metric_determinant_uu = None
	metric_determinant_dd = None

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

	def uu(self, i: int, j: int) -> Symbol:
		return self.metric_tensor_uu[i, j]
	
	def dd(self, i: int, j: int) -> Symbol:
		return self.metric_tensor_dd[i, j]

	def det_uu(self):
		return self.metric_determinant_uu

	def det_dd(self):
		return self.metric_determinant_dd

	@classmethod
	def minkowski_txyz(cls, units: UnitSystem):
		return cls(CoordinateSystem.txyz(), [[units.c**2, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]], "dd")

class ChristoffelSymbols:

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
		if not self._christoffel_symbols_udd_computed[i][k][l]:
			symbol = 0
			for m in range(4):
				symbol = symbol + Rational("1/2")*self.metric_tensor.uu(m,i)*(diff(self.metric_tensor.dd(k,m), self.coordinates.x(i))+diff(self.metric_tensor.dd(l,m), self.coordinates.x(k))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(m)))
			self.christoffel_symbols_udd[i,k,l] = simplify(symbol)
			self._christoffel_symbols_udd_computed[i][k][l] = True
		return self.christoffel_symbols_udd[i, k, l]
	
	def ddd(self, i, k, l):
		if not self._christoffel_symbols_ddd_computed[i][k][l]:
			self.christoffel_symbols_ddd[i,k,l] = simplify(Rational('1/2')*(diff(self.metric_tensor.dd(i,k), self.coordinates.x(l))+diff(self.metric_tensor.dd(i,l), self.coordinates.x(k))-diff(self.metric_tensor.dd(k,l), self.coordinates.x(i))))
			self._christoffel_symbols_ddd_computed[i][k][l] = True
		return self.christoffel_symbols_ddd[i, k, l]

	def compute(self):
		for i in range(4):
			for j in range(4):
				for k in range(4):
					self.udd(i, j, k)
					self.ddd(i, j, k)

class RiemannTensor:

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
		if not self._riemann_tensor_uddd_computed[rho][sig][mu][nu]:
			coefficient = diff(self.christoffel_symbols.udd(rho, nu, sig), self.coordinates.x(mu)) - diff(self.christoffel_symbols.udd(rho, mu, sig), self.coordinates.x(nu))
			for lam in self.coordinates.dimensions:
				coefficient = coefficient + self.christoffel_symbols.udd(rho, mu, lam)*self.christoffel_symbols.udd(lam, nu, sig) - self.christoffel_symbols.udd(rho, nu, lam)*self.christoffel_symbols.udd(lam, mu, sig)
			self.riemann_tensor_uddd[rho, sig, mu, nu] = simplify(coefficient)
			self._riemann_tensor_uddd_computed[rho][sig][mu][nu] = True
		return self.riemann_tensor_uddd[rho, sig, mu, nu]

	def dddd(self, rho, sig, mu, nu):
		if not self._riemann_tensor_dddd_computed[rho][sig][mu][nu]:
			coefficient = Rational('1/2')*(self.metric_tensor.dd(rho, nu).diff(self.coordinates.x(sig)).diff(self.coordinates(mu)) + self.metric_tensor.dd(sig, mu).diff(self.coordinates.x(rho)).diff(self.coordinates.x(nu))\
			-self.metric_tensor.dd(rho, mu).diff(self.coordinates.x(sig)).diff(self.coordinates.x(nu))-self.metric_tensor.dd(sig, nu).diff(self.coordinates.x(rho)).diff(self.coordinates.x(mu)))
			for n in range(4):
				for p in range(4):
					coefficient = coefficient + self.metric_tensor.dd(n, p)*(self.christoffel_symbols.udd(n, sig, mu)*self.christoffel_symbols.udd(p, rho, nu)-self.christoffel_symbols(n, sig, nu)*self.christoffel_symbols.udd(p, rho, mu))
			self.riemann_tensor_dddd[rho, sig, mu, nu] = simplify(coefficient)
			self._riemann_tensor_dddd_computed[rho][sig][mu][nu] = True
		return self.riemann_tensor_dddd[rho, sig, mu, nu]

class RicciTensor:

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
		if self.ricci_tensor_dd[mu, nu] is None:
			coefficient = 0
			for lam in range(4):
				coefficient = coefficient + self.riemann_tensor.uddd(lam, mu, lam, nu)
			self.ricci_tensor_dd[mu, nu] = simplify(coefficient)
		return self.ricci_tensor_dd[mu,nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		if self.ricci_tensor_uu[mu, nu] is None:
			coefficient = 0
			for rho in range(4):
				for sig in range(4):
					coefficient = coefficient + self.metric_tensor.uu(mu, rho)*self.metric_tensor.uu(nu, sig)*self.dd(rho, sig)
			self.ricci_tensor_uu[mu, nu] = simplify(coefficient)
		return self.ricci_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		raise RuntimeError("The developer needs to fix the RicciTensor.ud method which was never implemented.")

	def scalar(self) -> Symbol:
		if self.ricci_scalar is None:
			scalar = 0
			for mu in range(4):
				for nu in range(4):
					scalar = scalar + self.metric_tensor.uu(mu, nu) * self.dd(mu, nu)
			self.ricci_scalar = simplify(scalar)
		return self.ricci_scalar

class EinsteinTensor:

	metric_tensor: MetricTensor = None
	ricci_tensor: RicciTensor = None
	einstein_tensor_dd = Matrix([[None for i in range(4)] for j in range(4)])
	einstein_tensor_uu = Matrix([[None for i in range(4)] for j in range(4)])
	einstein_tensor_ud = Matrix([[None for i in range(4)] for j in range(4)])

	def __init__(self, ricci: RicciTensor) -> None:
		self.ricci_tensor = ricci
		self.metric_tensor = self.ricci_tensor.metric_tensor

	def dd(self, mu, nu):
		if self.einstein_tensor_dd[mu, nu] is None:
			self.einstein_tensor_dd[mu, nu] = simplify(self.ricci_tensor.dd(mu, nu) - Rational("1/2")*self.ricci_tensor.scalar()*self.metric_tensor.dd(mu, nu))
		return self.einstein_tensor_dd[mu, nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		if self.einstein_tensor_uu[mu, nu] is None:
			self.einstein_tensor_uu[mu, nu] = simplify(self.ricci_tensor.uu(mu, nu) - Rational("1/2")*self.ricci_tensor.scalar()*self.metric_tensor.uu(mu, nu))
		return self.einstein_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		raise RuntimeError("The developer needs to fix the EinsteinTensor.ud method which was never implemented.")

class StressEnergyMomentumTensor:

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
		if self.stress_energy_momentum_tensor_dd[mu, nu] is None:
			self.stress_energy_momentum_tensor_dd[mu, nu] = simplify((self.einstein_tensor.dd(mu, nu) + self.units.Lambda*self.metric_tensor.dd(mu, nu)) / self.units.kappa)
		return self.stress_energy_momentum_tensor_dd[mu, nu]

	def uu(self, mu: int, nu: int) -> Symbol:
		if self.stress_energy_momentum_tensor_uu[mu, nu] is None:
			self.stress_energy_momentum_tensor_uu[mu, nu] = simplify((self.einstein_tensor.uu(mu, nu) + self.units.Lambda*self.metric_tensor.uu(mu, nu)) / self.units.kappa)
		return self.stress_energy_momentum_tensor_uu[mu, nu]

	def ud(self, mu: int, nu: int) -> Symbol:
		raise RuntimeError("The developer needs to fix the StressEnergyMomentumTensor.ud method which was never implemented.")

	def compute_dd(self):
		for i in range(4):
			for j in range(4):
				self.dd(i, j)

	def compute_uu(self):
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

	def proper(i: int) -> Symbol:
		if self.proper_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.proper_geodesic_acceleration_vector[i] = accel
		return self.proper_geodesic_acceleration_vector[i]

	def coordinate(i: int) -> Symbol:
		if self.proper_geodesic_acceleration_vector[i] is None:
			accel = 0
			for mu in range(4):
				for nu in range(4):
					accel = accel - self.christoffel.udd(0, mu, nu)*self.coordinates.v(i)*self.coordinates.v(mu)*self.coordinates.v(nu) - self.christoffel.udd(i, mu, nu)*self.coordinates.w(mu)*self.coordinates.w(nu)
			self.proper_geodesic_acceleration_vector[i] = accel
		return self.proper_geodesic_acceleration_vector[i]

class Spacetime:

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