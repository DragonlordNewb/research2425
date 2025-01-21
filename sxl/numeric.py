from sympy import Symbol
from sxl import util
from typing import Union

Number = Union[float, int]

class InvalidUnitError(Exception):
	pass

class Constant(Symbol):

	def __init__(self, name: str, value: Number):
		Symbol.__init__(self, name)
		self.value = value

	def substitute(self, expression):
		return expression.subs(self.name, self.value)

class ConstantSet:

	THROWN_WARNING = False

	def __init__(self, **kwargs):
		self.constants = {}
		for key in kwargs.keys():
			const = UniversalConstant(key, kwargs[key])
			self.constants[key] = const

	def __iter__(self):
		return zip(list(self.constants.keys()), list(self.constants.values()))

	def __getitem__(self, name: str):
		if name not in self.constants.keys():
			if not self.THROWN_WARNING and util.Configuration.allow_unit_misname:
				print("sxl.numeric.UnitSystem.get: Warning: no such constant \"{}\" was registered. New UC with that name has been returned; this warning will not be shown again.".format(name))
				self.THROWN_WARNING = True
			elif not util.Configuration.allow_unit_misname:
				raise InvalidUnitError("No such unit \"{}\" was registered (with this UnitSystem).".format(name))
			return Symbol(name)
		return self.constants[name]

	def __setitem__(self, name: str, value: Number):
		self.constants[name] = value

	def substitute(self, expression):
		ex = expression
		for _, const in self:
			ex = const.substitute(ex)
		return ex

class ConstantMultiset:

	def __init__(self, *cs):
		self.sets = cs

	def __iter__(self):
		return iter(self.sets)

	def substitute(self, expression):
		ex = expression
		for s in self:
			ex = s.substitute(ex)
		return ex