import sys
import sympy as sp
import math
import time
import functools
import itertools

version = "1.0"

def tp(*args):
	# Trailoff print
	print(*args, end="")
	sys.stdout.flush()

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

def colorprint(s: str, *colors):
	print("".join(colors) + s + END)

class Configuration:

	verbose: bool = True
	autocompute: bool = False
	autocorrect: bool = True
	autoindex: bool = True
	silence: bool = False

	@staticmethod
	def set_verbose(value: bool) -> None:
		if type(value) != bool:
			raise TypeError("Must set sxl.util.Configuration.verbose to a bool value")
		Configuration.verbose = value

	@staticmethod
	def set_autocompute(value: bool):
		if type(value) != bool:
			raise TypeError("Must set sxl.util.Configuration.autocompute to a bool value")
		Configuration.autocompute = value

	@staticmethod
	def set_autoindex(value: bool):
		if type(value) != bool:
			raise TypeError("Must set sxl.util.Configuration.autoindex to a bool value")
		Configuration.autoindex = value
		
	@staticmethod
	def set_autocorrect(value: bool):
		if type(value) != bool:
			raise TypeError("Must set sxl.util.Configuration.autocorrect to a bool value")
		Configuration.autocorrect = value

def az(x):
	if x < 10:
		return "0" + str(x)
	else:
		return str(x)

def repr_time(dt):
	if dt < 1:
		return str(round(1000 * dt, 1)) + " ms"
	elif dt < 60:
		return str(round(dt, 1)) + " s"
	elif dt < 3600:
		return str(int(dt // 60)) + " m " + str(round(dt % 60, 1)) + " s"

class Loader:

	def __init__(self, desc: str):
		self.desc = desc
	
	def __enter__(self):
		print(self.desc, end="")
		sys.stdout.flush()
	
	def __exit__(self, _, __, ___):
		print("done.")

class ProgressBar:

	total: int
	current = 0
	fill: str
	desc: str
	st = None
	indent = 0

	def __init__(self, desc: str, total: int):
		self.desc = desc
		self.total = total
		self.fill = "#"

	def __enter__(self):
		self.st = time.time()
		self._update_bar()
		return self

	def __exit__(self, _, __, ___):
		if not Configuration.silence: print()

	def _update_bar(self, report=None):
		if Configuration.verbose:
			et = time.time()
			fill_count = self.current * 50 / self.total
			space_count = 50 - round(fill_count)
			sep_count = 50 - len(self.desc)
			report_str = ""
			if report is not None:
				report_str = "- " + report + "   "
			ratio_str = str(self.current) + "/" + str(self.total)
			if not Configuration.silence: tp("	"*self.indent + self.desc, " "*sep_count + "[" + self.fill*round(fill_count) + " "*space_count + "]", 
			ratio_str, " "*(8 - len(ratio_str)), "(" + str(round(fill_count*2, 1)) + "%)", repr_time(et - self.st), report_str, "\r")
		
	def done(self, report=None):
		self.current += 1
		self._update_bar(report)

def blank(n, d):
	if n == 1:
		return [None for _ in range(d)]
	return [blank(n - 1, d) for i in range(d)]

def expand_list(l):
	result = []
	for x in l:
		if type(x) == list:
			for y in expand_list(x):
				result.append(y)
		else:
			result.append(x)

def read_scalar(desc):
	desc = desc + " (scalar)"
	print(" " * (len(desc)+2), end="\r")
	print(desc, "[ ", end="")
	usr = input()
	print("\033[{}C\033[1A".format(len(usr)+11),end=" ] ")
	try:
		r = float(usr)
		print("Read as number: " + str(r))
		return r
	except:
		try:
			r = sp.sympify(usr)
			print("Read as expression: " + str(r))
			return r
		except Exception as e:
			print("Error: " + str(e) + ", please try again.")
			return read_scalar(desc)

def symind(n: int) -> list[tuple[int]]:
	for i in range(n):
		for j in range(i, n):
			yield (i, j)

def dissolve(l):
	for x in l:
		if type(x) in (list, tuple):
			for y in dissolve(x):
				yield y
		else:
			yield x

def allind(n, dimension) -> list[tuple[int]]:
	if n == 1:
		for x in [i for i in range(dimension)]:
			yield x
	else:
		for x in allind(n - 1, dimension):
			for i in range(dimension):
				yield tuple(dissolve([x, i]))