import sys
import sympy as sp

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

class ProgressBar:

    total: int
    fill: str
    desc: str

    def __init__(self, desc: str, total: int, fill: str="#"):
        self.desc = desc
        self.total = total
        self.fill = fill

    def __enter__(self):
        if Configuration.verbose:
            tp(self.desc, "- |" + " "*self.total + "|\r")
            tp(self.desc, "- |")
        return self

    def __exit__(self, _, __, ___):
        print()
        
    def done(self):
        if Configuration.verbose:
            tp(self.fill)