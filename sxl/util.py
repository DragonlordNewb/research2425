import sys
import sympy as sp
import math
import time

def tp(*args):
	# Trailoff print
	print(*args, end="")
	sys.stdout.flush()

class Configuration:

	verbose: bool = True
	autocompute: bool = False

	@staticmethod
	def set_verbose(value: bool) -> None:
		if type(value) != bool:
			raise TypeError("Must set sxl.spacetime.Configuration.verbose to a bool value")
		Configuration.verbose = value

	@staticmethod
	def set_autocompute(value: bool):
		if type(value) != bool:
			raise TypeError("Must set sxl.spacetime.Configuration.autocompute to a bool value")
		Configuration.autocompute = value

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

class ProgressBar:

	total: int
	current = 0
	fill: str
	desc: str
	st = None

	def __init__(self, desc: str, total: int, fill: str="#"):
		self.desc = desc
		self.total = total
		self.fill = fill

	def __enter__(self):
		self.st = time.time()
		self._update_bar()
		return self

	def __exit__(self, _, __, ___):
		print()

	def _update_bar(self, report=None):
		if Configuration.verbose:
			et = time.time()
			fill_count = self.current * 50 / self.total
			space_count = 50 - round(fill_count)
			sep_count = 50 - len(self.desc)
			report_str = ""
			if report is not None:
				report_str = "- " + report + "   "
			tp(self.desc, " "*sep_count + "[" + self.fill*round(fill_count) + " "*space_count + "]", str(self.current) + "/" + str(self.total), "(" + str(round(fill_count*2, 1)) + "%)", repr_time(et - self.st), report_str, "\r")
		
	def done(self, report=None):
		self.current += 1
		self._update_bar(report)