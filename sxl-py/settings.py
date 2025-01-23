from sympy import Symbol
from sympy import pi

autoindex = True
autocompute = True
autosolve = True
autodefine = True
cosmological_constant = False

class UnitSystem:

	def __init__(self, c: bool, G: bool, h: bool):
		self.c = c 
		self.G = G 
		self.h = h

	def is_normalized(const: str):
		if const == "c":
			return self.c 
		if const == "G":
			return self.G 
		if const == "h":
			return self.h

	def const(self, x: str):
		if x == "kappa":
			return 8 * pi * self.const("G") / self.const("c")**4
		if self.is_normalized(x):
			return 1
		return Symbol(x)

global_units = UnitSystem(False, False, False)