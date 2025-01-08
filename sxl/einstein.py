from sxl import spacetime
from sxl import settings
from sxl import util
from sympy import simplify
from sympy import Symbol
from sxl.spacetime import dim

class CosmologicalConstant(spacetime.Scalar):

	name = "cosmological"

	def compute(self, st):
		if settings.cosmological_constant:
			self.value = Symbol("Lambda")
		else:
			self.value = 0

class ChristoffelSymbols(spacetime.Rank3Tensor):

	name = "christoffel"
	# symmetry = "christoffel"

	def compute(self, st):
		metric = st.of("metric")
		with util.ProgressBar("Computing Christoffel symbols", (dim(self)**2 * (dim(self)+1)) / 2) as pb:
			for i in range(dim(self)):
				for j, k in util.symind(dim(self)):
					self.tensor_co[i][j][k] = self.tensor_co[i][k][j] = simplify(metric.co_diff(k, i, j) + metric.co_diff(j, i, k) - metric.co_diff(i, k, j)) / 2
					pb.done()

class RiemannTensor(spacetime.Rank4Tensor):

	name = "riemann"

	def compute(self, st):
		christoffel = st.of(ChristoffelSymbols)
		with util.ProgressBar("Computing Riemann tensor", dim(self)**4) as pb:
			for i in range(dim(self)):
				for j in range(dim(self)):
					for k in range(dim(self)):
						for l in range(dim(self)):
							r = christoffel.mixed_diff(k, i, l, j) - christoffel.mixed_diff(l, i, k, j)
							r = r + sum(
								(christoffel.mixed(i, k, m) * christoffel.mixed(m, l, j)) - (christoffel.mixed(i, l, m) * christoffel.mixed(m, k, j))
								for m in range(dim(self))
							)
							self.tensor_mixed[i][j][k][l] = simplify(r) # could be optimized
							pb.done()

class KretschmannScalar(spacetime.Scalar):

	name = "kretschmann"

	def compute(self, st):
		riemann = st.of(RiemannTensor)
		r = sum(
			riemann.contra(i, j, k, l) * riemann.co(i, j, k, l)
			for i in range(4)
			for j in range(4)
			for k in range(4)
			for l in range(4)
		)
		self.value = simplify(r)

class RicciTensor(spacetime.Rank2Tensor):

	name = "ricci tensor"

	def compute(self, st):
		riemann = st.of(RiemannTensor)
		with util.ProgressBar("Computing Ricci tensor", (dim(self)*(dim(self)+1))/2) as pb:
			for i, j in util.symind(dim(self)):
				r = sum(
					riemann.mixed(k, i, k, j)
					for k in range(dim(self))
				)
				self.tensor_co[i][j] = self.tensor_co[j][i] = simplify(r)
				pb.done()

class RicciScalar(spacetime.Scalar):

	name = "ricci scalar"

	def compute(self, st):
		ricci = st.of(RicciTensor)
		metric = st.of("metric")
		r = ricci.trace()
		self.value = r

class EinsteinTensor(spacetime.Rank2Tensor):

	name = "einstein"

	def compute(self, st):
		metric = st.of("metric")
		Rij = st.of(RicciTensor)
		R = st.of(RicciScalar)
		with util.ProgressBar("Computing Einstein tensor", (dim(self) * (dim(self)+1))/2) as pb:
			for i, j in util.symind(dim(self)):
				self.tensor_co[i][j] = self.tensor_co[j][i] = simplify(Rij.co(i, j) + (R() * metric.co(i, j))/2)
				self.tensor_contra[i][j] = self.tensor_contra[j][i] = simplify(Rij.contra(i, j) + (R() * metric.contra(i, j))/2)
				pb.done()

class StressEnergyMomentumTensor(spacetime.Rank2Tensor):

	name = "stress energy momentum"

	def compute(self, st):
		einstein = st.of(EinsteinTensor)
		cosmological = st.of(CosmologicalConstant)
		metric = st.of("metric")
		with util.ProgressBar("Computing stress-energy-momentum tensor", 10) as pb:
			for i, j in util.symind(dim(self)):
				dd = einstein.co(i, j) + (cosmological() * metric.co(i, j))
				uu = einstein.contra(i, j) + (cosmological() * metric.contra(i, j))
				self.tensor_co[i][j] = self.tensor_co[j][i] = dd
				self.tensor_contra[i][j] = self.tensor_contra[j][i] = uu
				pb.done()

EinsteinFieldEquationsParts = spacetime.DefinablePackage(
	CosmologicalConstant, 
	ChristoffelSymbols, 
	RiemannTensor,
	RicciTensor,
	RicciScalar,
	EinsteinTensor,
	StressEnergyMomentumTensor
)

class SchoutenTensor(spacetime.Rank2Tensor):
	
	name = "schouten"

	def compute(self, st):
		ricci = st.of(RicciTensor)
		scal = st.of(RicciScalar)
		metric = st.of("metric")

		for i in range(4):
			for j in range(4):
				uu = (ricci.contra(i, j) - (scal() * metric.contra(i, j) / 6)) / 2
				dd = (ricci.co(i, j) - (scal() * metric.co(i, j) / 6)) / 2
				self.tensor_co[i][j] = self.tensor_co[j][i] = dd 
				self.tensor_contra[i][j] = self.tensor_contra[j][i] = uu

class WeylTensor(spacetime.Rank4Tensor):

	name = "weyl"

	def compute(self, st):
		riemann = st.of(RiemannTensor)
		ricci = st.of(RicciTensor)
		scal = st.of(RicciScalar)
		metric = st.of("metric")

		for i in range(4):
			for k in range(4):
				for l in range(4):
					for m in range(4):
						self.tensor_co[i][k][l][m] = riemann.dddd(i, k, l, m) \
						+ ((
							(ricci.co(i, m) * metric.co(k, l)) - (ricci.co(i, l) * metric.co(k, m)) + (ricci.co(k, l) * metric.co(i, m)) - (ricci.co(k, m) * metric.co(i, l))
						) / 2) \
						+ ((
							scal() * ((metric.co(i, l) * metric.co(k, m)) - (metric.co(i, m) * metric.co(k, l)))
						) / 6)