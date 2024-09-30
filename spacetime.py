from sympy import *

class ChristoffelSymbols:

	metric = None
	symbol = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	symbol_derivatives = [[[[None for i in range(4)] for j in range(4)] for k in range(4)] for l in range(4)]

	def __init__(self, metric: "Metric") -> None:
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

class Metric:

	x0 = None
	x1 = None
	x2 = None
	x3 = None
	x = None
	tensor = None
	tensor_inverse = None
	tensor_derivatives = [[[None for i in range(4)] for j in range(4)] for k in range(4)]
	tensor_inverse_derivatives = [[[None for i in range(4)] for j in range(4)] for k in range(4)]

	christoffel_symbols: ChristoffelSymbols = None

	def __init__(self, coordinates: list[Symbol], metric: list[list["Expression"]]):
		self.x0, self.x1, self.x2, self.x3 = coordinates
		self.x = coordinates
		self.tensor = metric
		self.tensor_inverse = Matrix(metric).inv().tolist()
		self.christoffel_symbols = ChristoffelSymbols(self)

	def getDerivative(self, mu: int, nu: int, wrt: Symbol) -> "Expression":
		if self.tensor_derivatives[mu][nu][wrt] is None:
			self.tensor_derivatives[mu][nu][wrt] = diff(self.tensor[mu][nu], self.x[wrt])
		return self.tensor_derivatives[mu][nu][wrt]

	def getInverseDerivative(self, mu: int, nu: int, wrt: Symbol) -> "Expression":
		if self.tensor_inverse_derivatives[mu][nu][wrt] is None:
			self.tensor_inverse_derivatives[mu][nu][wrt] = diff(self.tensor_inverse[mu][nu], self.x[wrt])
		return self.tensor_inverse_derivatives[mu][nu][wrt]

if __name__ == "__main__":
	print("Testing Schwarzschild geometry")
	print("Assembling parameters ...", end="")
	x = symbols("t x y z")
	M, r = Symbol("M"), sqrt(x[1]**2 + x[2]**2 + x[3]**2)
	k = 1 - 2*M/r
	ik = 1/k
	mt = [[k, 0, 0, 0], [0, -ik, 0, 0], [0, 0, -ik, 0], [0, 0, 0, -ik]]
	print("done.\nPreparing spacetime ...", end="")
	metric = Metric(x, mt)
	print("done.\nChristoffel symbols:")
	print(metric.christoffel_symbols.get(1, 0, 0))