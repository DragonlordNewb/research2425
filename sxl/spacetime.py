from sympy import Matrix
from sympy import Function
from sympy import Symbol
from sympy import symbols
from sympy import Derivative
from sympy import diff
from sxl import error
from sxl import settings
from sxl import util
from functools import cache
from itertools import product

class Dimensional:

	dimension: int = None

	def __dim__(self):
		return self.dimension

def dim(d: Dimensional) -> int:
	r = d.__dim__()
	if r is None:
		raise error.DimensionalError("Dimensionality for this object not set.")
	if type(r) != int:
		raise error.DimensionalError("Dimensionality for this object was set to a non-int (invalid).")
	return r

def all_indices(rank, dimensions):
	return product(range(dimensions), repeat=rank)

def elementwise_add(a, b):
	l = len(a)

	c = []
	for i in range(l):
		if type(a[i]) == list:
			c.append(elementwise(a[i], b[i]))
		else:
			c.append(a[i] + b[i])
	return c

def elementwise_sub(a, b):
	l = len(a)

	c = []
	for i in range(l):
		if type(a[i]) == list:
			c.append(elementwise(a[i], b[i]))
		else:
			c.append(a[i] - b[i])
	return c

def scalar_multiply(a, s):
	l = len(a)

	c = []
	for i in range(l):
		if type(a[i]) == list:
			c.append(elementwise(a[i], s))
		else:
			c.append(a[i] * s)
	return c

def scalar_divide(a, s):
	l = len(a)

	c = []
	for i in range(l):
		if type(a[i]) == list:
			c.append(elementwise(a[i], s))
		else:
			c.append(a[i] / s)
	return c

class Coordinates(Dimensional):

	"""
	Describes a 4D coordinate system.
	"""

	def __init__(self, *coordinates):
		if len(coordinates) == 1:
			# I assume we're talking about at least 1+1D
			self.coordinate_symbols = symbols(coordinates[0])
		else:
			self.coordinate_symbols = list(map(Symbol, coordinates))
		self.dimension = len(self.coordinate_symbols)
		self.proper_time = Symbol("tau")

	def __repr__(self):
		return "<{}D coordinate system: {}>".format(dim(self), ", ".join(map(lambda x: x.name, self.coordinate_symbols)))

	def __iter__(self):
		return iter(self.coordinate_symbols)
	
	@cache
	def x(self, index: int) -> Symbol:
		return self.coordinate_symbols[index]

	@cache
	def inverse(self, name: Symbol | str) -> int:
		for i, s in enumerate(self):
			if s.name == name:
				return i
		return -1

class MetricTensor(Dimensional):

	"""
	Describes a 4D (+---) metric tensor.
	"""

	def __init__(self, m: list[list[Symbol]], coordinates: Coordinates) -> None:
		print(m)
		self.coordinates = coordinates
		self.metric_tensor_dd = m
		self.metric_tensor_uu = Matrix(m).inv().tolist()
		self.dimension = dim(self.coordinates)
	
	def __dim__(self):
		return self.dimension

	def __repr__(self):
		return "<MetricTensor with coordinates " + repr(self.coordinates) + ">"

	def co(self, mu=None, nu=None) -> Symbol:
		if mu == nu == None:
			return self.metric_tensor_dd
		return self.metric_tensor_dd[mu][nu]

	def contra(self, alpha=None, beta=None) -> Symbol:
		if alpha == beta == None:
			return self.metric_tensor_uu
		return self.metric_tensor_uu[alpha][beta]

	@cache
	def co_diff(self, d, mu, nu) -> Symbol:
		if type(d) == int:
			return diff(self.co(mu, nu), self.coordinates.x(d))
		return diff(self.co(mu, nu), d)

	@cache
	def contra_diff(self, d, alpha, beta) -> Symbol:
		if type(d) == int:
			return diff(self.contra(alpha, beta), self.coordinates.x(d))
		return diff(self.contra(alpha, beta), d)

	def ud(self, i=None, j=None):
		return 1 if i == j else 0

class Definable(Dimensional):

	name: str = None
	definable = True

	def compute(self, st: "Spacetime"):
		raise NotImplementedError("Computation not defined for this object.")

class DefinablePackage:

	def __init__(self, *parts):
		self.parts = parts

	def __iter__(self):
		return iter(self.parts)

class Scalar(Definable):

	"""
	Describes a scalar.
	"""

	def __init__(self, metric: MetricTensor, value=None):
		self.metric_tensor = metric
		self.coordinates = self.metric_tensor.coordinates
		self.value = value
		self.dimension = 0

	def __call__(self, metric: MetricTensor=None): # TODO: clean that up!! Not sure why but something is passing a positional arg to this elsewhere...
		return self.value

	def compute(self):
		pass

	@cache
	def diff(self, d):
		if type(d) == int:
			return diff(self.value, self.coordinates.x(d))
		return diff(self.value, d)

class Tensor(Definable):

	rank: int = None

	def __init__(self, metric: MetricTensor, t=None, indexing: str=None):
		self.metric_tensor = metric
		self.coordinates = self.metric_tensor.coordinates
		self.dimension = self.metric_tensor.dimension
		self.tensor_co = util.blank(self.rank, dim(self))
		self.tensor_contra = util.blank(self.rank, dim(self))
		self.tensor_mixed = util.blank(self.rank, dim(self))
		if self.name == None:
			if indexing == "co":
				self.tensor_co = t
			elif indexing == "contra":
				self.tensor_contra = t
			elif indexing == "mixed":
				self.tensor_mixed = t

	def solve(self):
		for comb in all_indices(self.rank, self.dimension):
			self.co(*comb)
			self.contra(*comb)
			self.mixed(*comb)

	def _extract(self, ls, *indices):
		raise NotImplementedError("Extraction not implemented on this Tensor subclass (this is a bad error).")

	def _raise_index(self, *indices):
		raise NotImplementedError("Index raising not implemented on this Tensor subclass (this is a bad error).")

	def _lower_index(self, *indices):
		raise NotImplementedError("Index lowering not implemented on this Tensor subclass (this is a bad error).")

	def _mix_index(self, *indices):
		raise NotImplementedError("Index mixing not implemented on this Tensor subclass (this is a bad error).")

	def co(self, *indices):
		if len(indices) == 0:
			return self.tensor_co
		elif len(indices) != self.rank:
			raise SyntaxError("Invalid number of indices (" + str(len(indices)) + ") for a rank-" + str(rank) + " tensor.")
		
		r = self._extract(self.tensor_co, *indices)
		if r is None:
			return self._lower_index(*indices)
		return r

	def co_diff(self, deriv, *indices):
		if type(deriv) == int:
			return diff(self.co(*indices), self.coordinates.x(deriv))
		return diff(self.co(*indices), deriv)

	def contra(self, *indices):
		if len(indices) == 0:
			return self.tensor_contra
		elif len(indices) != self.rank:
			raise SyntaxError("Invalid number of indices (" + str(len(indices)) + ") for a rank-" + str(rank) + " tensor.")
		
		r = self._extract(self.tensor_contra, *indices)
		if r is None:
			return self._lower_index(*indices)
		return r

	def contra_diff(self, deriv, *indices):
		if type(deriv) == int:
			return diff(self.contra(*indices), self.coordinates.x(deriv))
		return diff(self.contra(*indices), deriv)

	def mixed(self, *indices):
		if len(indices) == 0:
			return self.tensor_mixed
		elif len(indices) != self.rank:
			raise SyntaxError("Invalid number of indices (" + str(len(indices)) + ") for a rank-" + str(rank) + " tensor.")
		
		r = self._extract(self.tensor_mixed, *indices)
		if r is None:
			return self._mix_index(*indices)
		return r

	def mixed_diff(self, deriv, *indices):
		if type(deriv) == int:
			return diff(self.mixed(*indices), self.coordinates.x(deriv))
		return diff(self.mixed(*indices), deriv)

	def __add__(self, other):
		"""
		Add two tensors of the same rank and dimension.
		"""
		# if not issubclass(type(other), Tensor):
		#	raise TypeError("Can only add another Tensor.")
		if self.rank != other.rank or self.dimension != other.dimension:
			raise ValueError("Tensors must have the same rank and dimension to be added.")

		result = Tensor(self.metric_tensor)
		result.tensor_co = elementwise_add(self.tensor_co, other.tensor_co)
		result.tensor_contra = elementwise_add(self.tensor_contra, other.tensor_contra)
		result.tensor_mixed = elementwise_add(self.tensor_mixed, other.tensor_mixed)
		return result

	def __sub__(self, other):
		"""
		Subtract two tensors of the same rank and dimension.
		"""
		if not isinstance(other, Tensor):
			raise TypeError("Can only subtract another Tensor.")
		if self.rank != other.rank or self.dimension != other.dimension:
			raise ValueError("Tensors must have the same rank and dimension to be subtracted.")

		result = Tensor(self.metric_tensor)
		result.tensor_co = elementwise_sub(self.tensor_co, other.tensor_co)
		result.tensor_contra = elementwise_sub(self.tensor_contra, other.tensor_contra)
		result.tensor_mixed = elementwise_sub(self.tensor_mixed, other.tensor_mixed)
		return result

	def __mul__(self, scalar):
		"""
		Multiply a tensor by a scalar.
		"""
		if not isinstance(scalar, (int, float)):
			raise TypeError("Scalar must be a number.")
		
		result = Tensor(self.metric_tensor)
		result.tensor_co = scalar_multiply(self.tensor_co, scalar)
		result.tensor_contra = scalar_multiply(self.tensor_contra, scalar)
		result.tensor_mixed = scalar_multiply(self.tensor_mixed, scalar)
		return result

	def __truediv__(self, scalar):
		"""
		Divide a tensor by a scalar.
		"""
		if not isinstance(scalar, (int, float)):
			raise TypeError("Scalar must be a number.")
		if scalar == 0:
			raise ZeroDivisionError("Cannot divide by zero.")
		
		result = Tensor(self.metric_tensor)
		result.tensor_co = scalar_divide(self.tensor_co, scalar)
		result.tensor_contra = scalar_divide(self.tensor_contra, scalar)
		result.tensor_mixed = scalar_divide(self.tensor_mixed, scalar)
		return result

class Rank1Tensor(Tensor):

	rank = 1

	def _extract(self, ls, i):
		return ls[i]

	def _raise_index(self, i):
		r = sum(self.metric_tensor.contra(i, j) * self.co(j) for j in range(dim(self)))
		self.tensor_contra[i] = r 
		return r

	def _lower_index(self, i):
		r = sum(self.metric_tensor.co(i, j) * self.contra(j) for j in range(dim(self)))
		self.tensor_co[i] = r
		return r

	def _mix_index(self, i):
		return 0

	def norm(self):
		r = sum(
			self.metric_tensor.co(i, j) * self.contra(i) * self.contra(j)
			for i in range(dim(self))
			for j in range(dim(self))
		)
		return r

	def contra_mag(self):
		return sqrt(sum(i**2 for i in self.contra()))

	def mag(self): return self.contra_mag()

	def co_mag(self):
		return sqrt(sum(i**2 for i in self.co()))

class Rank2Tensor(Tensor):

	rank = 2
	symmetry: str = None

	trace_wrt_metric: Symbol = None

	def _extract(self, ls, i, j):
		return ls[i][j]

	def _raise_index(self, i, j):
		r = sum(
			self.metric_tensor.contra(i, k) * self.metric_tensor.contra(j, l) * self.co(k, l)
			for k in range(dim(self))
			for l in range(dim(self))
		)
		self.tensor_contra[i][j] = r 
		if self.symmetry == "symmetric":
			self.tensor_contra[j][i] = r 
		if self.symmetry == "antisymmetric":
			self.tensor_contra[j][i] = -r
		return r

	def _lower_index(self, i, j):
		r = sum(
			self.metric_tensor.co(i, k) * self.metric_tensor.co(j, l) * self.co(k, l)
			for k in range(dim(self))
			for l in range(dim(self))
		)
		self.tensor_contra[i][j] = r
		if self.symmetry == "symmetric":
			self.tensor_contra[j][i] = r 
		if self.symmetry == "antisymmetric":
			self.tensor_contra[j][i] = -r
		return r

	def _mix_index(self, i, j):
		r = sum(self.metric_tensor.contra(i, k) * self.co(k, j) for k in range(dim(self)))
		self.tensor_mixed[i][j] = r
		if self.symmetry == "symmetric":
			self.tensor_contra[j][i] = r 
		if self.symmetry == "antisymmetric":
			self.tensor_contra[j][i] = -r
		return r

	def trace(self):
		if self.trace_wrt_metric == None:
			self.trace_wrt_metric = sum(
				self.metric_tensor.contra(i, j) * self.co(i, j)
				for i in range(dim(self))
				for j in range(dim(self))
			)
		return self.trace_wrt_metric

class Rank3Tensor(Tensor):

	rank = 3
	symmetry: str = None

	def _extract(self, ls, i, j, k):
		return ls[i][j][k]

	def _raise_index(self, i, j, k):
		r = sum(
			self.metric_tensor.contra(i, l) * self.metric_tensor.contra(j, m) * self.metric_tensor.contra(k, n) * self.co(l, m, n)
			for l in range(dim(self))
			for m in range(dim(self))
			for n in range(dim(self))
		)
		self.tensor_contra[i][j][k] = r 
		if self.symmetry == "christoffel":
			self.tensor_contra[i][k][j] = r
		if self.symmetry == "reverse christoffel":
			self.tensor_contra[j][i][k] = r
		return r

	def _lower_index(self, i, j, k):
		r = sum(
			self.metric_tensor.co(i, l) * self.mixed(l, j, k)
			for l in range(dim(self))
			for m in range(dim(self))
			for n in range(dim(self))
		)
		self.tensor_co[i][j][k] = r 
		if self.symmetry == "christoffel":
			self.tensor_co[i][k][j] = r
		if self.symmetry == "reverse christoffel":
			self.tensor_co[j][i][k] = r
		return r

	def _mix_index(self, i, j, k):
		r = sum(self.metric_tensor.contra(i, l) * self.co(l, j, k) for l in range(dim(self)))
		self.tensor_mixed[i][j][k] = r 
		if self.symmetry == "christoffel":
			self.tensor_mixed[i][k][j] = r
		if self.symmetry == "reverse christoffel":
			self.tensor_mixed[j][i][k] = r
		return r

class Rank4Tensor(Tensor):

	rank = 4
	symmetry: str = None

	def _extract(self, ls, i, j, k, l):
		return ls[i][j][k][l]

	def _raise_index(self, i, j, k, l):
		r = sum(
			self.metric_tensor.contra(i, m) * self.metric_tensor.contra(j, n) * self.metric_tensor.contra(k, o) * self.metric_tensor.contra(l, p) * self.co(m, n, o, p)
			for m in range(dim(self))
			for n in range(dim(self))
			for o in range(dim(self))
			for p in range(dim(self))
		)
		self.tensor_contra[i][j][k][l] = r
		if self.symmetry == "riemann":
			self.tensor_contra[i][j][l][k] = -r
			self.tensor_contra[j][i][k][l] = -r
			self.tensor_contra[j][i][l][k] = self.tensor_contra[k][l][i][j] = r
		return r

	def _lower_index(self, i, j, k, l):
		r = sum(
			self.metric_tensor.contra(i, m) * self.mixed(m, j, k, l)
			for m in range(dim(self))
		)
		self.tensor_co[i][j][k][l] = r
		if self.symmetry == "riemann":
			self.tensor_contra[i][j][l][k] = -r
			self.tensor_contra[j][i][k][l] = -r
			self.tensor_contra[j][i][l][k] = self.tensor_contra[k][l][i][j] = r
		return r

	def _mix_index(self, i, j, k, l):
		r = sum(self.metric_tensor.contra(i, m) * self.co(m, j, k, l) for m in range(dim(self)))
		self.tensor_mixed[i][j][k][l] = r 
		if self.symmetry == "riemann":
			self.tensor_contra[i][j][l][k] = -r
			self.tensor_contra[j][i][k][l] = -r
			self.tensor_contra[j][i][l][k] = self.tensor_contra[k][l][i][j] = r
		return r
	
Vector = Tensor1 = Rank1Tensor
Tensor2 = Tensor = Rank2Tensor
Tensor3 = Rank3Tensor
Tensor4 = Rank4Tensor

class Manifold(Dimensional):

	"""
	Defines a manifold on which other things can be defined.
	"""
	
	_computed = True

	def __init__(self, metric: MetricTensor) -> None:
		self.metric_tensor = metric
		self.coordinates = self.metric_tensor.coordinates
		self.definitions = {"metric": self.metric_tensor}
		self.dimension = dim(self.metric_tensor)

	def _a(self, obj: Definable, ac) -> None:
		if hasattr(obj, "definable"):
			x = obj(self.metric_tensor)
			self.definitions[x.name] = x
			if settings.autocompute and ac:
				self[x.name].compute(self)
			else:
				self._computed = False
		elif type(obj) == DefinablePackage:
			for x in obj.parts:
				self.define(x)
		else:
			raise TypeError("Cannot define an object of type \"" + type(obj).__name__ + "\" on a manifold.")

	def define(self, obj):
		self._a(obj, True)

	def consider(self, obj):
		self._a(obj, False)

	def compute(self):
		for obj in self.definitions.values():
			obj.compute()
		self._computed = True

	def solve(self):
		if not self._computed:
			self.compute()
		for obj in self.definitions.values():
			obj.solve()

	def _of_by_name(self, name: str) -> Definable:
		if name not in self.definitions.keys():
			raise TypeError("No such object of name \"" + name + "\" defined on this spacetime.")
		return self.definitions[name]

	def _of_by_type(self, t: type) -> Definable:
		for d in self.definitions:
			if type(self.definitions[d]) == t:
				return self.definitions[d]
		if settings.autodefine:
			self.define(t(self.metric_tensor))
			return self._of_by_type(t)
		raise TypeError("No such object of type \"" + str(t.__name__) + "\" defined on this spacetime.")

	@cache
	def of(self, identifier: str | type) -> "Definable":
		if type(identifier) == type: # I hate this line
			return self._of_by_type(identifier)
		if type(identifier) == str:
			return self._of_by_name(identifier)
		raise SyntaxError("Invalid identifier type.")

	def __getitem__(self, identifier):
		return self.of(identifier)

	def covariant_derivative(self, x, i: int):
		if type(x) == Scalar:
			return diff(self.value, self.coordinates.x(i))
		if type(x) == Vector:
			christoffel = self.of("christoffel")
			return Vector(self.metric_tensor, [diff(x.co(j), self.coordinates.x(i)) + sum(x.co(k) * christoffel.mixed(k, i, j) for k in range(dim(self)))], indexing="co")

	def contravariant_derivative(self, x, i: int):
		return sum(self.metric_tensor.contra(i, j) * self.covariant_derivative(x, j) for j in range(dim(self)))