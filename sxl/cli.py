from blessed import Terminal
from sxl import *
import sys

term = Terminal()
lib = library.Library()
opts = {x: i for i, x in enumerate(list("123456789abcdefghijklmnopqrstuvwxyz"))}
manifold: spacetime.Manifold = None

def clarify(elements):
	print("Please clarify:")
	for i, elements in enumerate(elements[:36]):
		print("\t{}\t{}".format(list(opts.keys())[i], elements))
	with term.cbreak(), term.hidden_cursor():
		print("Press any option key to continue...", end="")
		sys.stdout.flush()
		while True:
			k = term.inkey()
			if opts[k] < len(elements):
				print("\r", " "*34)
				return opts[k]
			else:
				print("Invalid option, please try again.         ")

def parse_command(cmd):

	global manifold

	cmds = cmd.split(" ")

	if cmds[0] == "exit":
		print("Quitting.")
		exit()

	elif cmds[0] == "clear":
		print(term.clear)

	elif cmds[0] == "search":
		print("Searching library ...", end="")
		sys.stdout.flush()
		results = lib.search(*cmds[1:])
		l = len(results)
		if l == 1:
			s = ""
		else:
			s = "s"
		print("\rLibrary searched successfully; {} result{}.".format(l, s))
		for result in results:
			print("\t" + result)

	elif cmds[0] == "manifold":
		if cmds[1] in ("help", "-h", "--help"):
			print(manual.cli.HELP_MANIFOLD)
			return

		if cmds[1] == "create":
			if "-h" in cmds or "--help" in cmds:
				print(manual.cli.HELP_MANIFOLD_CREATE)
				return

			results = lib.search(*cmds[2:], metric=True)

			if len(results) == 1:
				metric = lib[results[0]]
			else:
				choice = clarify(results)
				print("Clarified the chosen metric:", results[choice])
				metric = lib[results[choice]]

			print("Attempting to create manifold ...")
			manifold = spacetime.Manifold(metric)
			print("Successfully created manifold.")

		if cmds[1] == "define":
			if "-h" in cmds or "--help" in cmds:
				print(manual.cli.HELP_MANIFOLD_DEFINE)
				return

			if manifold is None:
				print("Cannot define anything, manifold is not created yet. Try \"manifold create <metric search terms>\" to make one.")
				return

			results = lib.search(*cmds[2:], geometric=True)

			if len(results) == 1:
				obj = lib[results[0]]
			else:
				choice = clarify(results)
				print("Clarified the chosen metric:", results[choice])
				obj = lib[results[choice]]

			print("Attempting to create manifold ...")
			manifold.define(obj)
			print("Successfully created manifold.")

		if cmds[1] == "report":
			pass

	else:
		print("Invalid command.")

def loop():
	print(term.home + term.clear)
	print("Spacetime Exploration Library v" + str(util.version))
	print("Type any command to continue. ----\n")
	while True:
		cmd = input(" > ")
		print()
		parse_command(cmd)
		print()