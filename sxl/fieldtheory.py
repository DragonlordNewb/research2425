from abc import ABC 
from abc import abstractmethod
from sxl.spacetime import Scalar
from sxl.spacetime import Tensor
from sxl.spacetime import Vector
from sxl.spacetime import Tensor2
from sxl.spacetime import Tensor3
from sxl.spacetime import Manifold


class Field(ABC):

	spin: int
	manifold: Manifold

	@abstractmethod
	def force(self, coupling, four_velocity: Vector, four_position: Vector):
		raise NotImplementedError("How did you manage to use this method?")

class ScalarField(Field):

	spin = 0

	def __init__(self, field: Scalar) -> None:
		self.field = field

	def force(self, coupling, four_velocity: Vector)