from typing import Any, Iterable, Callable
from itertools import combinations
from math import floor
import random

AB_ERROR = """Alpha/beta pair did not correctly generate.

A known issue is that Python does not deal well with very large ints and
exceedingly large values (by Python's bit standard) may fail to produce 
correct alpha/beta pairs.

If you are seeing this message you have exceeded Python's current ability 
to handle ints this large although hopefully the author will update the 
code soon, or you can try it yourself.

As of this writing, the function has been verified to work for all ints
smaller than a million, so if you're using those numbers in practice
you should really just fix the floating point math.

In fact, you should ask yourself why you're using those numbers in the
first place, since the algorithm is O(n^4). You do NOT want to use this
algorithm for anything important.
"""

DOUBLES = "doubles"
TRIPLES = "triples"
QUADRUPLES = "quadruples"

def alpha_beta_rep(n: int) -> tuple[int, int]:
	"""
	It turns out that all integers n>2 can be represented in terms
	of two integers, alpha (a) and beta (b), with b={0,1,2}. The
	formula is
	
		n = 3a + 2b

	and for any integer n there exist integers a and b that satisfy
	this relationship.

	For example,

		n | 3 | 4 | 5 | 6 | 7 | 8 | 9 |     | n
		a | 1 | 0 | 1 | 2 | 1 | 2 | 3 | ... | (n-4) - 2*floor(n-4 / 3) | approx. O(n/3)=O(n)
		b | 0 | 2 | 1 | 0 | 2 | 1 | 0 |     | -n mod 3                 | approx. O(1)

	Note that this is essentially only repeated addition of 2, 3, and
	4 a specific number of times.

	Technically 2 is representable this way but that case is trivial
	regardless. Another weird note is that the pattern of alpha,
	starting from n=3, matches the rhyme scheme of Dante Alighieri's
	Divine Comedy.
	"""

	if n > 2:
		alpha, beta = (n-4) - (2*floor((n-4) / 3)), -n % 3
		assert n == (3*alpha) + (2*beta), AB_ERROR
		return alpha, beta
	return None

def alpha(n: int) -> int:
	return (n-4) - (2*floor((n-4) / 3))

def beta(n: int) -> int:
	return -n % 3

class OperationCounter:
	"""
	A counter for operations.

	This class is a very simple counter which, when invoked with
	the ~ operand, increments a stored number. This is specifically
	used to count the number of operations a given function/program
	takes so as to get an empirical result as to its complexity.

	The function/program itself needs to accept an OperationCounter
	as an argument. For example,

		def go(..., oc: OperationCounter=0) -> int:
			...
			for op_num in range(op_count):
				~oc
			...
			return 1

	In the event that the operation count isn't cared for, a default
	argument of 0 (or any int) can be given, since ints have ~ as an
	operand.
	"""

	def __init__(self) -> None:
		self.operations = 0

	def increment(self) -> None:
		"""
		Creates the notation "~OperationCounter" to increment
		the counter and add one to the internal count.
		"""
		self.operations += 1

class Graph:

	"""
	A simple Graph data structure.

	Arbitrary vertices are assigned arbitrary names (objects that
	implement __eq__), and the graph is initialized with a list of
	the edges between them.
	"""

	"""
	# ===== UTILITY ===== #

	Functions for manipulating the data structure in Python. Few of
	these will have any operation-counting, except for .adjacency 
	and .neighborhood.

	As such, checking for two vertices' adjacency and finding the
	neighborhood of a vertex are considered O(1) operations.
	"""

	def __init__(self, edges: list[tuple[Any, Any]]) -> None:
		self.edges = edges
		self.all_vertices = None
		list(self.vertices())

	def adjacency(self, x: Any, y: Any, oc: OperationCounter=0) -> bool:
		"""
		Return whether or not the given edge is in the graph.

		Assumed to be an O(1) lookup.
		"""

		oc.increment()
		return (x, y) in self.edges or (y, x) in self.edges if x != y else False # just in case

	def vertices(self) -> Iterable[Any]:
		"""
		Iterate through all the vertices in the graph.

		Having access to all the vertices is assumed to
		be an O(0) operation -- listing them all should
		be part of the problem statement.

		On the first pass, they are also cached.
		"""

		if self.all_vertices is None:
			self.all_vertices = []
			for edge in self.edges:
				for x in edge:
					if x in self.all_vertices:
						continue
					self.all_vertices.append(x)
					yield x
		else:
			for vertex in self.all_vertices:
				yield vertex

	def neighborhood(self, vertex: Any, oc: OperationCounter=0) -> list[Any]:
		"""
		Return a list of vertices that have at least one edge with
		the given vertex.
		"""

		results = []
		for other_vertex in self.vertices():
			if other_vertex == vertex:
				continue
			if self.adjacency(vertex, other_vertex, oc):
				results.append(other_vertex)
		return results

	def subgraph(self, vertices: list[int]) -> "Graph":
		new_edges = []
		for x, y in self.edges:
			if x in vertices and y in vertices:
				new_edges.append((x, y))
		return Graph(new_edges)

	"""
	# ===== CLIQUE-FINDING ===== #

	Here are functions that all implement operation counting
	and are intended to help with clique-finding.

	None of these functions use any local variables and
	if they return anything except a boolean or a set of vertices
	they will return an iterable so as not to use any more memory
	than is absolutely strictly necessary. No lists are formed,
	so no extra memory is used.

	This makes the memory requirement of the program O(1), if I'm
	not mistaken.
	"""

	# === Small-clique lookup === #

	def all_doubles(self, oc: OperationCounter=0) -> Iterable[set[Any, Any]]:
		"""
		Go through all the edges, for consistency.
		
		Worst-case time to finish: (n-1)n = O(n^2)
		"""

		for edge in self.edges:
			oc.increment() # doesn't end up mattering
			yield set(edge)

	def all_triples(self, oc: OperationCounter=0) -> Iterable[set[Any, Any, Any]]:
		"""
		Naively iterate through all the triples in the graph.

		By "naive", it is meant that no result caching takes place
		so some triples (e.g. {x, y, z} and {y, x, z}) are effectively
		duplicated.

		Worst-case time to finish: (n-2)(n-1)n = O(n^3)
		"""

		for x in self.vertices():
			for y in self.vertices():
				if x == y:
					continue
				for z in self.vertices():
					if x == z or y == z:
						continue

					# Established: x != y, y != z, x != z

					if self.adjacency(x, y, oc) and self.adjacency(x, z, oc) and self.adjacency(y, z, oc):
						yield set((x, y, z))
	
	def all_quadruples(self, oc: OperationCounter=0) -> Iterable[set[Any, Any, Any, Any]]:
		"""
		Naively iterate through all the quadruples in the graph. This
		is naive in the same way the previous method is.

		Worst-case time to finish: (n-3)(n-2)(n-1)n = O(n^4)
		"""

		for w in self.vertices():
			for x in self.vertices():
				if w == x:
					continue
				for y in self.vertices():
					if w == y or x == y:
						continue
					for z in self.vertices():
						if w == z or x == z or y == z:
							continue
						
						# Established: w, x, y, z are different

						if self.adjacency(w, x, oc) \
								and self.adjacency(w, y, oc) \
								and self.adjacency(w, z, oc) \
								and self.adjacency(x, y, oc) \
								and self.adjacency(x, z, oc) \
								and self.adjacency(y, z, oc):
							yield set((w, x, y, z))

	def all_quintuples(self, oc: OperationCounter=0) -> Iterable[set[Any, Any, Any, Any, Any]]:
		"""
		See previous methods.
		
		This is the largest required because 3+2=5. I don't have
		a better explanation. I guess it guarantees that the recursive
		.link method always has base cases for n.
		"""

		for v in self.vertices():
			for w in self.vertices():
				if v == w:
					continue

				for x in self.vertices():
					if x == v or x == w:
						continue

					for y in self.vertices():
						if y == x or y == w or y == v:
							continue

						for z in self.vertices():
							if z == v or z == w or z == x or z == y:
								continue

							if self.adjacency(v, w, oc) \
									and self.adjacency(v, x, oc) \
									and self.adjacency(v, y, oc) \
									and self.adjacency(v, z, oc) \
									and self.adjacency(w, x, oc) \
									and self.adjacency(w, y, oc) \
									and self.adjacency(w, z, oc) \
									and self.adjacency(x, y, oc) \
									and self.adjacency(x, z, oc) \
									and self.adjacency(y, z, oc):
								yield set((w, x, y, z))
							

	def link(self, clique: set, with_type: str, oc: OperationCounter) -> Iterable[set]:
		"""
		Link a clique with all other possible cliques of a low size.
		This entails going through all cliques of that other size and
		checking to see if each vertex in the other clique is adjacent
		to each vertex of the first clique. If so, then the two cliques
		make up a single larger clique. Otherwise, it's nothing special.

		The "low size" means that only other cliques of size 2 (any pair)
		or size 3 (triangles/triples) or size 4 (quadruples) are allowed.

		But remember from the alpha_beta_rep function that it is actually
		possible to represent any integer as a repeated sum of 2, 3, and 4
		for some number of repetitions of each number. So this method can
		actually produce cliques of any size (that the graph permits) in
		the same time it would take to come up with all of those smaller
		cliques.

		This function is however naive in that it certainly repeats some
		cliques, because the functions that pull up the doubles/triples/
		quadruples are also naive in the same way. That turns out not to
		be important in the end, though.

		clique: a size n clique, as a set.
		with_type: one of the constants at the top of the file, referring
					to "all cliques of size k".
		returns: an iterable of all the size n+k cliques!
		"""

		iterator: Iterable = None
		
		if with_type == DOUBLES:
			f = self.all_doubles(oc)
		elif with_type == TRIPLES:
			f = self.all_triples(oc)
		elif with_type == QUADRUPLES:
			f = self.all_quadruples(oc)

		flag: bool = None

		for other_clique in f:
			flag = False
			
			# Check to make sure the vertices of other_clique are all a part of the main clique.
			# Due to the nature of the .adjacency method, if the cliques overlap it will return False
			# and the other_clique will be flagged, guaranteeing that the algorithm doesn't try to
			# link overlapping cliques.
			for x in other_clique:
				for y in clique:
					if not self.adjacency(x, y, oc):
						flag = True
						break

			if flag:
				continue

			yield clique.union(other_clique) # A size n+k clique.

	def cliques_of_size(self, n: int, oc: OperationCounter) -> Iterable[set]:
		"""
		An iterable that, through alpha/beta representation, takes the 
		size-2, size-3, and size-4 cliques and links them together until
		size-n cliques are obtained.
		
		If none are obtained/exist it doesn't do anything, big shocker.

		For n>4, the algorithm runs like this...

		1. Figure out the alpha/beta representation of n.
		2. For each triple (of which there are O(n^3)):
			a) Link more triples into it until it is of size n - 2b (O(n), see alpha_beta_rep).
				If it can't reach size n, go to the next triple.
			b) If b>0, link doubles/quadruples into it (of which there are O(n^2) and O(n^4)
				respectively) to get it to size n.
			c) Yield the new size-n clique.
		
		A good prediction places this at around O(n^4), or at least somewhere within P. Given
		that at worst O(n) links have to be done and the most expensive link loop is O(n^4) for
		the quadruples, the worst case bound would seem to be O(n^5).

		If this is to be believed, then all other NP-complete problems can be solve in at best
		O(n^5) with this algorithm. This is terrifyingly fast for an algorithm that solves NP-complete
		problems, but it is by no means fast compared to something like list sort.
		"""

		escape: bool = None

		if n == 2:
			for edge in self.all_doubles(oc):
				yield edge
		elif n == 3:
			for triple in self.all_triples(oc):
				yield triple
		elif n == 4:
			for quadruple in self.all_quadruples(oc):
				yield quadruple
		elif n == 5:
			for quintuple in self.all_quintuples(oc):
				yield quintuple
		elif n > 5:
			for clique in self.cliques_of_size(n - 3, oc):
				for new_clique in link(clique, TRIPLES):
					yield new_clique
		else:
			raise ValueError(f"Invalid input for clique size: {n}. Must be an int >= 2.")

def generate_graph_with_cliques(num_vertices):
    vertices = [chr(65 + i) for i in range(num_vertices)]  # 'A', 'B', ..., up to needed count

    edges = set()

    # Add a 3-clique: vertices[0], vertices[1], vertices[2]
    clique3 = vertices[0:3]
    for edge in combinations(clique3, 2):
        edges.add(tuple(sorted(edge)))

    # Add a 4-clique: vertices[3], vertices[4], vertices[5], vertices[6]
    if num_vertices >= 7:
        clique4 = vertices[3:7]
        for edge in combinations(clique4, 2):
            edges.add(tuple(sorted(edge)))

    # Add some sparse edges among remaining vertices to avoid new cliques
    remaining = vertices[7:]
    random.seed(42)  # For reproducibility
    while len(edges) < num_vertices + 5:  # Sparse random edges
        a, b = random.sample(vertices, 2)
        edge = tuple(sorted((a, b)))
        if edge not in edges:
            edges.add(edge)

    return list(edges)


if __name__ == "__main__":
	# Generate 20 graphs for sizes from 6 to 26
	print("Generating graphs >-<")
	graphs = {n: generate_graph_with_cliques(n) for n in range(6, 27)}
	print("Graphs generated. ^w^")