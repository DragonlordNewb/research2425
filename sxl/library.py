from sxl import spacetime
from sxl import einstein
from sxl import geodesics
from sympy import symbols, sin, Function

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

c, G, M, r, th = symbols("c G M r theta")
schwarzschild = 1 + (2 * G * M / (r * c**2))
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

@Library.register("Schwarzschild metric", ["3+1D", "4D", "metric", "black hole", "vacuum"])
def schwarzschild_metric():
	return spacetime.MetricTensor([
		[schwarzschild * c**2, 0, 0, 0],
		[0, -1/schwarzschild, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

@Library.register("Spherically-symmetric metric", ["3+1D", "4D", "metric"])
def spherically_symmetric():
	return spacetime.MetricTensor([
		[fr, 0, 0, 0],
		[0, -1/gr, 0, 0],
		[0, 0, -r**2, 0],
		[0, 0, 0, -r**2 * (sin(th)**2)]
	], trtp_coords())

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

@Library.register("everything", ["geometric", "EFEs"])
def everything():
	return einstein.EinsteinFieldEquationsParts