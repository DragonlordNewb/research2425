from sxl import spacetime

"""
Here, all forces will be treated as 4-forces produced by the 
curvature of gauge fields of some sort.
"""

class Observer:

	manifold: spacetime.Manifold
	position: spacetime.Vector # coordinate position differential from origin
	velocity: spacetime.Vector # proper velocity - dx/dtau

	@classmethod
	def at_rest(self, manifold: spacetime.Manifold, position: spacetime.Vector):
		self.manifold
		self.position = position
		self.velocity = spacetime.Vector(self.manifold)
		