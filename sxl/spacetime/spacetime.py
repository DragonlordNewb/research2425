import sympy

class CoordinateSystem:

	x, x0, x1, x2, x3 = None, None, None, None, None
	v, v0, v1, v2, v3 = None, None, None, None, None

	def __init__(self, name0, name1, name2, name3):
		self.x = sympy.symbols(" ".join([name0, name1, name2, name3]))
		self.x0, self.x1, self.x2, self.x3 = self.x
		self.v = sympy.symbols(" ".join(["v_" + name0, "v_" + name1, "v_" + name2, "v_" + name3]))
		self.v0, self.v1, self.v2, self.v3 = self.v

class MetricTensor:

	coords: CoordinateSystem = None
	tensor = None
	tensor_inverse = None
	tensor_derivatives = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	tensor_mixed_derivatives = [[[[None for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]
	tensor_inverse_derivatives = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	tensor_determinant = None
	tensor_inverse_determinant = None

	def __init__(self, coords: CoordinateSystem, metric: list[list["Expression"]]):
		self.coords = coords
		self.tensor = metric
		self.tensor_inverse = sympy.Matrix(metric).inv().tolist()

	def get_dd(self, i, j):
		return self.tensor[i][j]

	def get_uu(self, i, j):
		if self.tensor_inverse is None:
			self.tensor_inverse = sympy.Matrix(self.tensor).inv().tolist()
		return self.tensor_inverse[i][j]

	def getDerivative(self, mu: int, nu: int, wrt: sympy.Symbol) -> "Expression":
		if self.tensor_derivatives[mu][nu][wrt] is None:
			self.tensor_derivatives[mu][nu][wrt] = sympy.diff(self.tensor[mu][nu], self.coords.x[wrt])
		return self.tensor_derivatives[mu][nu][wrt]

	def getMixedDerivative(self, mu: int, nu: int, wrt1: int, wrt2: int):
		if self.tensor_mixed_derivatives[mu][nu][wrt1][wrt2] is None:
			self.tensor_mixed_derivatives[mu][nu][wrt1][wrt2] = sympy.diff(sympy.diff(self.tensor[mu][nu], self.coords.x[wrt1]), self.coords.x[wrt2])

	def getInverseDerivative(self, mu: int, nu: int, wrt: sympy.Symbol) -> "Expression":
		if self.tensor_inverse_derivatives[mu][nu][wrt] is None:
			self.tensor_inverse_derivatives[mu][nu][wrt] = sympy.diff(self.tensor_inverse[mu][nu], self.coords.x[wrt])
		return self.tensor_inverse_derivatives[mu][nu][wrt]

	def getDeterminant(self):
		if self.tensor_determinant is None:
			self.tensor_determinant = sympy.Matrix(self.tensor).det()
		return self.tensor_determinant()

	def getInverseDeterminant(self):
		if self.tensor_inverse_determinant is None:
			self.tensor_inverse_determinant = sympy.Matrix(self.tensor_inverse).det()
		return self.tensor_inverse_determinant

class ChristoffelSymbols:

	metric = None
	symbol = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	symbol_derivatives = [[[[None for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, metric: "MetricTensor") -> None:
		self.metric = metric

	def get(self, i, k, l):
		if self.symbol[i][k][l] is None:
			# Compute the symbol
			self.symbol[i][k][l] = sum(
				self.metric.tensor_inverse[i][m]
				* (self.metric.getDerivative(m, k, l) + self.metric.getDerivative(m, l, k) - self.metric.getDerivative(k, l, m)) 
				for m in range(4)
			) / 2
		return self.symbol[i][k][l]

	def getDerivative(self, i, k, l, wrt):
		if self.symbol_derivatives[i][k][l][wrt] is None:
			self.symbol_derivatives[i][k][l][wrt] = sympy.diff(self.get(i, k, l), self.metric.coords.x[wrt])
		return self.symbol_derivatives[i][k][l][wrt]

class RiemannTensor:

	metric: MetricTensor
	tensor_uddd = [[[[None for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, metric: MetricTensor) -> None:
		self.metric = metric

	def get(self, i: int, k: int, l: int, m: int):
		if self.tensor_uddd[i][k][l][m] is None:
			self.tensor_uddd[i][k][l][m] = (self.metric.getMixedDerivative(i,m,k,l)+self.metric.getMixedDerivative(k,l,i,m)-self.metric.getMixedDerivative(i,l,k,m)-self.metric.getMixedDerivative(k,m,i,l)) / 2
		return self.tensor_uddd[i][k][l][m]

class RicciTensor:

	metric = None
	christoffel = None
	riemann = None
	initializedWith = None
	tensor_dd = [[None for i in range(4)] for j in range(4)]
	tensor_uu = [[None for i in range(4)] for j in range(4)]
	scalar = None

	def __init__(self, initializer, metric: MetricTensor) -> None:
		self.metric = metric
		if type(initializer) == ChristoffelSymbols:
			self.christoffel = initializer
			self.initializedWith = ChristoffelSymbols
		else:
			self.riemann = initializer
			self.initializedWith = RiemannTensor
	
	def get_dd(self, i: int, j: int):
		if self.tensor_dd[i][j] is None:
			if self.initializedWith == ChristoffelSymbols:
				self.tensor_dd[i][j] = sum(
					self.christoffel.getDerivative(a, i, j, a) for a in range(4)
				) - sum(
					self.christoffel.getDerivative(a, a, i, j) for a in range(4)
				) + sum(
					sum(
						self.christoffel.get(a,a,b) * self.christoffel.get(b,i,j)
						- self.christoffel.get(a,i,b) * self.christoffel.get(b,a,j)
						for b in range(4)
					) for a in range(4)
				)
			else:
				self.tensor_dd[i][j] = sum(
					self.riemann.get(k, i, k, j) for k in range(4)
				)
		return self.tensor_dd[i][j]

	def get_uu(self, i: int, j: int):
		if self.tensor_uu[i][j] is None:
			self.tensor_uu[i][j] = sum(
				sum(
					self.metric.get_uu(i, a) * self.metric.get_uu(j, b) * self.get_dd(a, b)
					for b in range(4)
				) for a in range(4)
			)
		return self.tensor_uu[i][j]

	def getScalar(self):
		if self.scalar is None:
			self.scalar = sum(
				sum(
					self.metric.get_uu(i, j) * self.get_dd(i, j)
					for j in range(4)
				) for i in range(4)
			)
		return self.scalar
	
class EinsteinTensor:

	ricci: RicciTensor = None
	tensor_dd = [[None for i in range(4)] for j in range(4)]
	tensor_uu = [[None for i in range(4)] for j in range(4)]

	def __init__(self, metric: MetricTensor, ricci: RicciTensor) -> None:
		self.metric = metric
		self.ricci = ricci

	def get_dd(self, i: int, j: int):
		if self.tensor_dd[i][j] is None:
			self.tensor_dd[i][j] = self.ricci.get_dd(i, j) \
			- (self.ricci.metric.get_dd(i, j) * self.ricci.getScalar() / 2)
		return self.tensor_dd[i][j]

	def get_uu(self, i: int, j: int):
		if self.tensor_uu[i][j] is None:
			self.tensor_uu[i][j] = self.ricci.get_uu(i, j) \
			- (self.ricci.metric.getInverse(i, j) * self.ricci.getScalar() / 2)
		return self.tensor_uu[i][j]

class StressEnergyMomentumTensor:

	einstein: EinsteinTensor = None
	units: "UnitSystem" = None
	tensor_dd = [[None for i in range(4)] for j in range(4)]
	tensor_uu = [[None for i in range(4)] for j in range(4)]

	def __init__(self, einstein: EinsteinTensor, units: "UnitSystem") -> None:
		self.einstein = einstein
		self.units = units

	def get_dd(self, i: int, j: int):
		if self.tensor_dd[i][j] is None:
			self.tensor_dd[i][j] = (self.einstein.get_dd(i,j)+(self.units.Lambda*self.einstein.ricci.metric.get_dd(i,j)))/self.units.kappa
		return self.tensor_dd[i][j]

	def get_uu(self, i: int, j: int):
		if self.tensor_uu[i][j] is None:
			self.tensor_uu[i][j] = (self.einstein.get_dd(i,j)+(self.units.Lambda*self.einstein.ricci.metric.get_uu(i,j)))/self.units.kappa
		return self.tensor_uu[i][j]

class GeodesicAccelerationVector:

	metric: MetricTensor = None
	christoffel: ChristoffelSymbols
	vector_dxds = [None for i in range(4)]
	vector_dxdt = [None for i in range(4)]

	def __init__(self, metric: MetricTensor, christoffel: ChristoffelSymbols):
		self.metric = metric
		self.christoffel = christoffel

	def get_dxds(self, i: int):
		if self.vector_dxds[i] is None:
			self.vector_dxds[i] = -sum(
				sum(
					self.christoffel.get(i, a, b) * self.metric.v[a] * self.metric.v[b]
					for b in range(4)
				) for a in range(4)
			)
		return self.vector_dxds[i]

	def get_dxdt(self, i: int):
		if self.vector_dxdt[i] is None:
			self.vector_dxdt[i] = sum(
				sum(
					self.christoffel.get(0, a, b) * self.metric.v[a] * self.metric.v[b] * self.metric.v[i]
					for b in range(4)
				) for a in range(4)
			) - self.get_dxds(i)
		return self.vector_dxdt[i]

class UnitSystem:

	c = None
	G = None
	h = None
	Lambda = None
	kappa = None

	def __init__(self, normc: bool, normG: bool, normh: bool, normLambda: bool):
		self.c = 1 if normc else sympy.Symbol("c")
		self.G = 1 if normG else sympy.Symbol("G")
		self.h = 1 if normh else sympy.Symbol("h")
		self.Lambda = 0 if normLambda else sympy.Symbol("Lambda")
		self.kappa = 8 * sympy.pi * self.G / self.c**4

class Spacetime:

	units: UnitSystem = None
	metric: MetricTensor = None
	christoffel: ChristoffelSymbols = None
	riemann: RiemannTensor = None
	ricci: RicciTensor = None
	einstein: EinsteinTensor = None
	stress_energy_momentum: StressEnergyMomentumTensor = None

	geodesic_acceleration: GeodesicAccelerationVector = None

	def __init__(self, metric: MetricTensor, units: UnitSystem, calculateRicciWith: type=ChristoffelSymbols):
		self.metric = metric
		self.units = units
		self.christoffel = ChristoffelSymbols(self.metric)
		self.riemann = RiemannTensor(self.metric)
		if calculateRicciWith == ChristoffelSymbols:
			self.ricci = RicciTensor(self.christoffel, self.metric)
		else:
			self.ricci = RicciTensor(self.riemann, self.metric)
		self.einstein = EinsteinTensor(self.metric, self.ricci)
		self.stress_energy_momentum = StressEnergyMomentumTensor(self.einstein, self.units)
		self.geodesic_acceleration = GeodesicAccelerationVector(self.metric, self.christoffel)