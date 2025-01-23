from blessed import Terminal
from sxl import *
import sys
import sympy
import os

from sxl.spacetime import dim, rank

class InvalidCommand(Exception):
	pass

class ScriptExecutionError(Exception):
	pass

class IncompleteOrInvalidCommand(Exception):
	pass

class InvalidCommandSyntax(Exception):
	pass

class InvalidArgument(Exception):
	pass

class SXL:

	term = Terminal()
	lib = library.Library()
	opts = {x: i for i, x in enumerate(list("123456789abcdefghijklmnopqrstuvwxyz"))}
	manifold: spacetime.Manifold = None

	def confirm(self, desc: str) -> bool:
		print(desc, "(y/n)", end="")
		sys.stdout.flush()
		with self.term.cbreak(), self.term.hidden_cursor():
			while True:
				k = self.term.inkey()
				if k == "y":
					print(desc, self.term.lime("(yes)"))
					return True
				if k == "n":
					print(desc, self.term.red("(no) "))
					return False

	def clarify(self, elements):
		print("Please clarify:")
		for i, elements in enumerate(elements[:36]):
			print("\t{}\t{}".format(list(self.opts.keys())[i], elements))
		with self.term.cbreak(), self.term.hidden_cursor():
			print("Press any option key to continue...", end="")
			sys.stdout.flush()
			while True:
				k = self.term.inkey()
				if self.opts[k] < len(elements):
					print("\r", " "*34)
					return self.opts[k]
				else:
					print("Invalid option, please try again.         ")

	def parse_command(self, cmd, raise_errors: bool=False):

		cmds = cmd.split(" ")

		ncmds = []
		for word in cmds:
			if word == "//":
				break
			elif "//" in word:
				s = ""
				for i in range(len(word) - 2):
					if word[i + 2] == "//":
						break
					else:
						s = s + word[i]
				ncmds.append(s)
				break
			else:
				ncmds.append(word)

		cmds = ncmds

		if len(cmds) == 0:
			return

		if "-q" in cmds or "--quiet" in cmds:
			util.Configuration.silence = True 

		if cmds[0] == "exit":
			print("Quitting.")
			exit()

		elif cmds[0] == "clear":
			print(self.term.clear)

		elif cmds[0] == "echo":
			if "-q" not in cmds and "--quiet" not in cmds: print(*cmds[1:])

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
				raise IncompleteOrInvalidCommand("Incomplete command, need to specify a subcommand. See \"manifold --help\" for more info.")

			if cmds[1] in ("help", "-h", "--help"):
				print(manual.cli.HELP_MANIFOLD)
				return

			elif cmds[1] in ("create", "c"):
				if len(cmds) <= 2:
					raise IncompleteOrInvalidCommand("Incomplete command, need to specify a metric. Try \"manifold create schwarzschild\" or see \"manifold create --help\".")

				if "-h" in cmds or "--help" in cmds:
					print(manual.cli.HELP_MANIFOLD_CREATE)
					return

				results = self.lib.search(*cmds[2:], metric=True)

				if len(results) == 1:
					metric = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					if "-q" not in cmds and "--quiet" not in cmds: print("Clarified the chosen metric:", results[choice])
					metric = self.lib[results[choice]]

				if "-q" not in cmds and "--quiet" not in cmds: print("Attempting to create manifold ...")
				self.manifold = spacetime.Manifold(metric)
				if "-q" not in cmds and "--quiet" not in cmds: print("Successfully created manifold.")

			elif cmds[1] in ("define", "d"):
				if len(cmds) <= 2:
					raise IncompleteOrInvalidCommand("Incomplete command, need to specify what to define. Try \"manifold define everything\" or see \"manifold define --help\".")

				if "-h" in cmds or "--help" in cmds:
					print(manual.cli.HELP_MANIFOLD_DEFINE)
					return

				if self.manifold is None:
					raise IncompleteOrInvalidCommand("Cannot define anything, manifold is not created yet. Try \"manifold create <metric search terms>\" to make one.")

				results = self.lib.search(*cmds[2:], geometric=True)

				if len(results) == 1:
					obj = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					print("Clarified the chosen object:", results[choice])
					obj = self.lib[results[choice]]

				if "-q" not in cmds and "--quiet" not in cmds: print("Attempting to define object(s) on manifold ...")
				self.manifold.define(obj)
				if "-q" not in cmds and "--quiet" not in cmds: print("Done.")

			elif cmds[1] in ("report", "r"):
				
				# Check for bad requests/calls for help

				if len(cmds) <= 2:
					raise IncompleteOrInvalidCommand("Incomplete command, need to specify what to report on. Try \"manifold report metric\" or see \"manifold report --help\".")

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
						raise InvalidCommandSyntax("Malformed command.")
						return

					for x in cmds[ioff+1:]:
						if x[0] == "-":
							break
						indices.append(x)

					if len(indices) == 0:
						raise InvalidCommandSyntax("No indices supplied, try adding indices (like 00, 12, 0101) after the -i flag.")
				
				else:
					search_terms = cmds[2:]

				# Search for the object, clarify if needed

				results = self.lib.search(*search_terms, geometric=True)

				if len(results) == 1:
					obj_type = self.lib[results[0]]
				else:
					choice = self.clarify(results)
					print("Clarified the chosen object:", results[choice])
					obj_type = self.lib[results[choice]]

				obj = self.manifold.of(obj_type)

				# Resolve mf r --all/-a

				if "--co" not in cmds and "--contra" not in cmds and "--mixed" not in cmds:
					raise InvalidCommandSyntax("Need to specify exactly one index type (none specified).")

				if "-a" in cmds or "--all" in cmds:
					for indices in util.allind(obj.rank, dim(obj)):
						print("Indices:", indices)
						if "--co" in cmds:
							sympy.pprint(obj.co(*indices))
						if "--contra" in cmds:
							sympy.pprint(obj.contra(*indices))
						if "--mixed" in cmds:
							sympy.pprint(obj.mixed(*indices))
						print("")
					return

				# Parse the indices

				if len(indices) == 1:
					if indices[0].isnumeric:
						indices = list(map(int, list(indices[0])))
					
				else:
					for i, x in enumerate(indices):
						inv = self.manifold.of(spacetime.MetricTensor).coordinates.inverse(x)
						if inv == -1:
							raise InvalidCommandSyntax("Invalid coordinate name \"{}\"".format(x))
							return
						indices[i] = inv

				# We can trace some tensors without indices so check for that quick

				if "--trace" in cmds:
					if not hasattr(obj, "trace"):
						raise InvalidArgument("Identified object does not have a trace associated with it.")
					sympy.pprint(obj.trace())
					return

				# Check for indexing errors

				if obj.rank > len(indices):
					raise InvalidCommandSyntax("Too few indices supplied, try adding more after the -i flag.")
				if obj.rank < len(indices):
					raise InvalidCommandSyntax("Too many indices supplied, try adding fewer after the -i flag.")

				# Print out the associated value, now that we've got the object and indices

				if type(obj) == spacetime.Scalar:
					sympy.pprint(obj())
				if "--co" in cmds:
					sympy.pprint(obj.co(*indices))
				if "--contra" in cmds:
					sympy.pprint(obj.contra(*indices))
				if "--mixed" in cmds:
					sympy.pprint(obj.mixed(*indices))

			else:
				raise IncompleteOrInvalidCommand("Incomplete or invalid command. See \"manifold --help\" for more info.")

		elif cmds[0] in ("runscript", "run"):
			path = []
			for x in cmds[1:]:
				if x[0] == "-":
					break
				path.append(x)
			path = " ".join(path)
			if os.path.exists(path):
				with open(path, "r") as f:
					script = f.read().split("\n")
				for n, ln in enumerate(script):
					if ln == "":
						continue

					if "-q" in cmds or "--quiet" in cmds:
						lnf = ln + " -q"
					else:
						lnf = ln

					try:
						self.parse_command(lnf.strip())
					except Exception as e:
						if "-p" in cmds or "--pess" in cmds or "--pessimist" in cmds:
							print(self.term.red("Aborting script execution: script error ({}) on line {}: \"{}\"".format(e, n+1, ln)))
							raise ScriptExecutionError("Script error ({}) on line {}: \"{}\"".format(e, n+1, ln))
						elif "-o" in cmds or "--opt" in cmds or "--optimist" in cmds:
							print(self.term.yellow("Warning: script error ({}) on line {}: \"{}\"".format(e, n+1, ln)))
						else:
							if self.confirm(self.term.yellow("Warning: script error ({}) on line {}: \"{}\", continue?".format(e, n+1, ln))):
								raise ScriptExecutionError("Script error ({}) on line {}: \"{}\"".format(e, n+1, ln))
			else:
				raise OSError("No such file exists (\"{}\")".format(path))

		else:
			raise InvalidCommand("Invalid command.")

	def loop(self):
		if "-v" in sys.argv:
			print(self.term.home + self.term.clear)
			self.lib.verify()
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
			except InvalidCommand as e:
				print("Invalid command: {}".format(e.args[0]))
			except ScriptExecutionError as e:
				print("Script execution error: {}".format(e.args[0]))
			except IncompleteOrInvalidCommand as e:
				print("Incomplete or invalid command: {}".format(e.args[0]))
			except InvalidCommandSyntax as e:
				print("Invalid command syntax: {}".format(e.args[0]))
			except InvalidArgument as e:
				print("Invalid argument: {}".format(e.args[0]))
			except OSError as e:
				print("OS error: {}".format(e.args[0]))
			except KeyboardInterrupt:
				print("\nStopped (by keyboard interrupt, \"{}\").           ".format(cmd))
			except Exception as e:
				raise e
			finally:
				if util.Configuration.silence and "-q" in cmd:
					util.Configuration.silence = False
				print()