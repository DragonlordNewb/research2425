from sxl.spacetime import *

DEFAULT_DT = 0.001

class Observer(ABC):

	position: Vector4 # the time coordinate represents external time lapse, the space coordinates represent actual position
	coordinate_velocity: Vector3
	proper_velocity: Vector4
	spacetime: Spacetime
	
	def __init__(self, metric: MetricTensor, position: Vector3 | Vector4, velocity: Vector3 | Vector4):
		if type(position) == Vector3:
			self.position = Vector4(metric, "u", 0, position.x(1), position.x(2), position.x(3))
		elif type(position) == Vector4:
			self.position = position
		else:
			raise TypeError("Position must be a vector type.")
		
		if type(velocity) == Vector3:
			self.coordinate_velocity = velocity
			self.proper_velocity = Vector4(metric, "u", self.spacetime.proper_time_lapse(velocity, self.position), None, None, None)
			self.proper_velocity.vector_u[1] = self.lorentz_factor() * self.coordinate_velocity.x(1)
			self.proper_velocity.vector_u[2] = self.lorentz_factor() * self.coordinate_velocity.x(2)
			self.proper_velocity.vector_u[3] = self.lorentz_factor() * self.coordinate_velocity.x(3)

	def correct_proper_velocity(self):
		self.proper_velocity = Vector4(self.spacetime.metric_tensor, "u", self.spacetime.proper_time_lapse(self.coordinate_velocity, self.position), None, None, None)
		self.proper_velocity.vector_u[1] = self.lorentz_factor() * self.coordinate_velocity.x(1)
		self.proper_velocity.vector_u[2] = self.lorentz_factor() * self.coordinate_velocity.x(2)
		self.proper_velocity.vector_u[3] = self.lorentz_factor() * self.coordinate_velocity.x(3)

	def lorentz_factor(self):
		return self.proper_velocity.u(0)
	
	def apply_coordinate_time(self, dt: float):
		self.position = self.position + self.coordinate_velocity*dt
		self.position.vector_u[0] += dt
	
	def apply_proper_time(self, dtau: float):
		self.position = self.position + self.proper_velocity*dtau
	
	def apply_coordinate_acceleration(self, a: Vector3, dt: float):
		self.coordinate_velocity = self.coordinate_velocity + a*dt
		alpha = a / (self.lorentz_factor()**3)
		dtau = dt / self.lorentz_factor()
		self.proper_velocity = self.proper_velocity + alpha*dtau

	def apply_proper_acceleration(self, alpha: Vector4, dtau: float):
		self.proper_velocity = self.proper_velocity + alpha*dtau
		a = alpha * self.lorentz_factor()**3
		dt = dtau * self.lorentz_factor()
		self.coordinate_velocity = self.coordinate_velocity + a*dt