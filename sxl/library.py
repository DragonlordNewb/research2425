from sxl import spacetime
from sxl import einstein
from sxl import geodesics
from sympy import symbols, sin, Function, Symbol

class Library:

	items: dict[str] = {}

	def search(self, *strings, **filters) -> list[str]:
		results = {}
		flag = None
		score = None

		for key, tags in self.items:
			flag = False
			score = 0

			for string in strings:
				if string.lower() in key.lower():
					score += 10
				for tag in tags:
					if string.lower() in tag.lower():
						score += 1
				for f in filters.keys():
					if (filters[f] and f not in tags) or (not filters[f] and f in tags):
						score -= 100

			if score > 0:
				results[key] = score

		return list(dict(sorted(results.items(), key=lambda item: item[1])).keys())[::-1]

	def _get(self, name):
		for key, _ in self.items:
			if name == key:
				return self.items[(key, _)]
			
		sr = self.search(name)
		if len(sr) == 0:
			raise NameError("Couldn\'t find anything in library about " + name + ".")
		return sr[0]

	def get(self, name):
		return self._get(name)()

	def __getitem__(self, name):
		return self.get(name)

	@classmethod
	def register(cls, name: str, tags: list[str]):
		def decorator(tcls):
			cls.items[(name, tuple(tags))] = tcls
			return tcls
		return decorator

titems = {
	("a", ("b", "c", "d")): 1,
	("e", ("f", "b", "c")): 2,
	("g", ("h", "i", "d")): 3
}

# ===== DEFAULT CONTENT ===== #

t, U, a, c, G, M, r, th, z, R = symbols("t U a c G M r theta z R")
Mt = Function("M")(Symbol("t"))
schwarzschild = 1 + (2 * G * M / (r * c**2))
sch_t = 1 + (2 * G * Mt / (r * c**2))
fr = Function("f")(r)
gr = Function("g")(r)

# === Coordinates === $

@Library.register("rectangular coordinates", ["3+1D", "4D", "cartesian", "coords"])
def txyz_coords():
	return spacetime.Coordinates("t x y z")

@Library.register("cylindrical coordinates", ["3+1D", "4D","symmetric", "axial", "coords"])
def trtz_coords():
	return spacetime.Coordinates("t r theta z")

@Library.register("spherical coordinates", ["3+1D", "4D", "symmetric", "coords"])
def trtp_coords():
	return spacetime.Coordinates("t r theta phi")

@Library.register("foliated cylindrical coordinates", ["2+1D", "3D", "foliation", "foliated", "coords"])
def trz_coords():
	return spacetime.Coordinates("t r z")

@Library.register("foliated spherical coordinates", ["2+1D", "3D", "foliation", "foliated", "coords"])
def tro_coords():
	return spacetime.Coordinates("t r Omega")

@Library.register("drive coordinates", ["3+1D", "4D", "coords", "warp"])
def tzRt_coords():
	return spacetime.Coordinates("t z R theta")

# === Metrics === #

# Minkowski

@Library.register("rectangular Minkowski metric", ["3+1D", "4D", "metric", "flat", "vacuum"])
def rectangular_minkowski():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1, 0, 0],
		[0, 0, -1, 0],
		[0, 0, 0, -1]
	], txyz_coords())

@Library.register("cylindrical Minkowksi metric", ["3+1D", "4D", "metric", "flat", "vacuum"])
def cylindrical_minkowski():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -1]
	], trtz_coords())

@Library.register("spherical Minkowski metric", ["3+1D", "4D", "metric", "flat", "vacuum"])
def spherical_minkowski():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

# Schwarzschild

@Library.register("Schwarzschild metric", ["3+1D", "4D", "metric", "black hole", "vacuum"])
def schwarzschild_metric():
	return spacetime.MetricTensor([
		[schwarzschild * c**2, 0, 0, 0],
		[0, -1/schwarzschild, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Time-varying Schwarzschild metric", ["3+1D", "4D", "metric", "black hole", "vacuum"])
def schwarzschild_metric_tv():
	return spacetime.MetricTensor([
		[sch_t * c**2, 0, 0, 0],
		[0, -1/sch_t, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Linearly-inflating Schwarzschild metric", ["3+1D", "4D", "metric", "black hole", "vacuum"])
def lin_inf_sch():
	return spacetime.MetricTensor([
		[(1 + (2 * G * t * a / (r * c**2))) * c**2, 0, 0, 0],
		[0, -1/(1 + (2 * G * a * t / (r * c**2))), 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Spherically-symmetric metric", ["3+1D", "4D", "metric", "spherical"])
def spherically_symmetric():
	return spacetime.MetricTensor([
		[fr, 0, 0, 0],
		[0, -1/gr, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Schwarzschild-alike metric", ["3+1D", "4D", "metric", "spherical"])
def sch_alike():
	return spacetime.MetricTensor([
		[fr, 0, 0, 0],
		[0, -1/fr, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Spherically-symmetric dilation field", ["3+1D", "4D", "metric", "spherical"])
def spherically_symmetric_dilation():
	return spacetime.MetricTensor([
		[fr, 0, 0, 0],
		[0, -1, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Spherically-symmetric contraction field", ["3+1D", "4D", "metric", "spherical"])
def spherically_symmetric_contraction():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1/gr, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("C1 warp bubble", ["warp", "3+1D", "4D", "metric", "spherical"])
def wb_c1():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1/((U * c**2 * r**2)/3 + a/r + 1), 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("C2 warp bubble", ["warp", "3+1D", "4D", "metric", "spherical"])
def wb_c2():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1/((U * c**2 / r**2) + a/r + 1), 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

# Drive coordinates

@Library.register("drive-coordinates Minkowski", ["3+1D", "4D", "metric", "flat", "vacuum", "warp"])
def drive_minkowski():
	return spacetime.MetricTensor([
		[c**2, 0, 0, 0],
		[0, -1 - z**2/(R**2 - z**2), R*z/(R**2 - z**2), 0],
		[0, R*z/(R**2 - z**2), -R**2/(R**2 - z**2), 0],
		[0, 0, 0, -(R**2 - z**2)]
	], tzRt_coords())

# === Geometrical objects === #

@Library.register("Christoffel symbols", ["geometric", "rank-3", "tensor", "connection", "coefficients", "EFEs"])
def c_symbols():
	return einstein.ChristoffelSymbols

@Library.register("Riemann tensor", ["geometric", "rank-4", "tensor"])
def rie_tensor():
	return einstein.RiemannTensor

@Library.register("Ricci tensor", ["geometric", "tensor", "rank-2", "symmetric", "EFEs"])
def ric_tensor():
	return einstein.RicciTensor

@Library.register("Ricci scalar", ["geometric", "tensor", "rank-0", "scalar", "EFEs"])
def ric_scalar():
	return einstein.RicciTensor

@Library.register("Einstein tensor", ["geometric", "tensor", "rank-2", "symmetric", "EFEs"])
def ein_tensor():
	return einstein.EinsteinTensor

@Library.register("stress-energy-momentum tensor", ["geometric", "sem", "tensor", "rank-2", "symmetric", "EFEs"])
def sem_tensor():
	return einstein.StressEnergyMomentumTensor

@Library.register("approximate stress-energy-momentum tensor", ["geometric", "sem", "tensor", "rank-2", "symmetric", "EFEs"])
def sem_tensor_approx():
	return einstein.ApproximateSEMTensor

@Library.register("everything", ["geometric", "EFEs"])
def everything():
	return einstein.EinsteinFieldEquationsParts