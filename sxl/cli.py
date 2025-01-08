from blessed import Terminal
from sxl import *
import sys
import sympy
import os

class SXL:

	term = Terminal()
	lib = library.Library()
	opts = {x: i for i, x in enumerate(list("123456789abcdefghijklmnopqrstuvwxyz"))}
	manifold: spacetime.Manifold = None

	def clarify(self, elements):
		print("Please clarify:")
		for i, elements in enumerate(elements[:36]):
			print("\t{}\t{}".format(list(opts.keys())[i], elements))
		with self.term.cbreak(), self.term.hidden_cursor():
			print("Press any option key to continue...", end="")
			sys.stdout.flush()
			while True:
				k = self.term.inkey()
				if opts[k] < len(elements):
					print("\r", " "*34)
					return opts[k]
				else:
					print("Invalid option, please try again.         ")

	def parse_command(self, cmd):

		cmds = cmd.split(" ")

		if cmds[0] == "exit":
			print("Quitting.")
			exit()

		elif cmds[0] == "clear":
			print(self.term.clear)

		elif cmds[0] == "search":
			print("Searching library ...", end="")
			sys.stdout.flush()
			results = self.lib.search(*cmds[1:])
			l = len(results)
			if l == 1:
				s = ""
			else:
				s = "s"
			print("\rLibrary searched successfully; {} result{}.".format(l, s))
			for result in results:
				print("\t" + result)

		elif cmds[0] in ("manifold", "mf"):

			if len(cmds) <= 1:
				print("Incomplete command, need to specify a subcommand. See \"manifold --help\" for more info.")
				return

			if cmds[1] in ("help", "-h", "--help"):
				print(manual.cli.HELP_MANIFOLD)
				return

			elif cmds[1] in ("create", "c"):
				if len(cmds) <= 2:
					print("Incomplete command, need to specify a metric. Try \"manifold create schwarzschild\" or see \"manifold create --help\".")

				if "-h" in cmds or "--help" in cmds:
					print(manual.cli.HELP_MANIFOLD_CREATE)
					return

				results = self.lib.search(*cmds[2:], metric=True)

				if len(results) == 1:
					metric = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					print("Clarified the chosen metric:", results[choice])
					metric = self.lib[results[choice]]

				print("Attempting to create manifold ...")
				self.manifold = spacetime.Manifold(metric)
				print("Successfully created manifold.")

			elif cmds[1] in ("define", "d"):
				if len(cmds) <= 2:
					print("Incomplete command, need to specify what to define. Try \"manifold define everything\" or see \"manifold define --help\".")

				if "-h" in cmds or "--help" in cmds:
					print(manual.cli.HELP_MANIFOLD_DEFINE)
					return

				if self.manifold is None:
					print("Cannot define anything, manifold is not created yet. Try \"manifold create <metric search terms>\" to make one.")
					return

				results = self.lib.search(*cmds[2:], geometric=True)

				if len(results) == 1:
					obj = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					print("Clarified the chosen object:", results[choice])
					obj = self.lib[results[choice]]

				print("Attempting to create manifold ...")
				self.manifold.define(obj)
				print("Successfully created manifold.")

			elif cmds[1] in ("report", "r"):
				
				# Check for bad requests/calls for help

				if len(cmds) <= 2:
					print("Incomplete command, need to specify what to report on. Try \"manifold report metric\" or see \"manifold report --help\".")

				if "-h" in cmds or "--help" in cmds:
					print(manual.cli.HELP_MANIFOLD_REPORT)

				# Parse command into search terms, flags, indices, etc.

				search_terms = []
				indices = []
				ioff = -1

				if "-i" in cmds or "--indices" in cmds:
					for i, x in enumerate(cmds[2:]):
						if x in ("-i", "--indices"):
							ioff = i + 2
							break
						elif x[0] != "-":
							search_terms.append(x)

					if ioff == -1:
						print("Malformed command.")
						return

					for x in cmds[ioff+1:]:
						indices.append(x)

					if len(indices) == 0:
						print("No indices supplied, try adding indices (like 00, 12, 0101) after the -i flag.")
						return
				
				else:
					search_terms = cmds[2:]

				# Parse the indices

				if len(indices) == 1:
					if indices[0].isnumeric:
						indices = list(map(int, list(indices[0])))
					
				else:
					for i, x in enumerate(indices):
						inv = self.manifold.of(spacetime.MetricTensor).coordinates.inverse(x)
						if inv == -1:
							print("Invalid coordinate name \"{}\"".format(x))
							return
						indices[i] = inv

				# Search for the object, clarify if needed

				results = self.lib.search(*search_terms, geometric=True)

				if len(results) == 1:
					obj_type = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					print("Clarified the chosen object:", results[choice])
					obj_type = self.lib[results[choice]]

				obj = self.manifold.of(obj_type)

				# Check for indexing errors

				if obj.rank > len(indices):
					print("Too few indices supplied, try adding more after the -i flag.")
				if obj.rank < len(indices):
					print("Too many indices supplied, try adding fewer after the -i flag.")

				# Print out the associated value, now that we've got the object and indices

				if type(obj) == spacetime.Scalar:
					sympy.pprint(obj())
				if "--co" in cmds:
					sympy.pprint(obj.co(*indices))
				if "--contra" in cmds:
					sympy.pprint(obj.contra(*indices))
				if "--mixed" in cmds:
					sympy.pprint(obj.mixed(*indices))
				if "--trace" in cmds and obj_type == spacetime.Rank2Tensor:
					sympy.pprint(obj.trace())

			else:
				print("Incomplete or invalid command. See \"manifold --help\" for more info.")

		elif cmds[0] in ("runscript", "run"):
			if os.path.exists(" ".join(cmds[1:]))

		else:
			print("Invalid command.")

	def loop(self):
		print(self.term.home + self.term.clear)
		print("Spacetime Exploration Library v" + str(util.version))
		print("Type any command to continue. ----\n")
		while True:

			try:
				cmd = input(" > ")
			except KeyboardInterrupt:
				print("\rQuitting.                     ")
				exit()
			except Exception as e:
				raise e

			print()

			try:
				self.parse_command(cmd)
			except KeyboardInterrupt:
				print("\nStopped (by keyboard interrupt, \"{}\").           ".format(cmd))
			except Exception as e:
				raise e
			finally:
				print()