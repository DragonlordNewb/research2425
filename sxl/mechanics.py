from sxl import spacetime
from sxl import observer
from sympy import Matrix
from sympy import cos
from sympy import sin
from typing import Union

CLIPPED = "CLIPPED" # "the point is inside the object"
CONTACT = "CONTACT" # "the point is EXACTLY on the surface of the object"
OUTSIDE = "OUTSIDE" # "the point is outside the object"

CollisionStatus = Union[CLIPPED, CONTACT, OUTSIDE]

class Shape:

    parameters: dict[str] = None
    comoving_observer: observer.Observer = None
    _cached_R = None
    _last_angle = None

    def __init__(self, comover: observer.Observer, **parameters) -> None:
        self.parameters = parameters
        self.comoving_observer = comover

    def centroid(self) -> spacetime.GeneralFourVector:
        return self.comoving_observer.position
    
    # Collision checking

    def transform_to_local(self, point: spacetime.GeneralFourVector) -> spacetime.GeneralFourVector:
        if self._last_angle is None or self._last_angle != self.comoving_observer.angle:
            rot = self.comoving_observer.angle
            theta_x, theta_y, theta_z = rot.u(1), rot.u(2), rot.u(3)

            R_x = Matrix([
                [1, 0, 0],
                [0, cos(theta_x), -sin(theta_x)],
                [0, sin(theta_x), cos(theta_x)]
            ])

            R_y = Matrix([
                [cos(theta_y), 0, sin(theta_y)],
                [0, 1, 0],
                [-sin(theta_y), 0, cos(theta_y)]
            ])

            R_z = Matrix([
                [cos(theta_z), -sin(theta_z), 0],
                [sin(theta_z), cos(theta_z), 0],
                [0, 0, 1]
            ])

            # Combine rotations (z first, then y, then x)
            self._cached_R = R_z * R_y * R_x

        c = self.centroid()
        x = Matrix([point.x(i) - c.x(i) for i in (1, 2, 3)])
        xprime = self._cached_R * x
        return spacetime.GeneralFourVector(c.x(0), xprime[0], xprime[1], xprime[2])
    
    def simple_collision(self, point: spacetime.GeneralFourVector) -> CollisionStatus:
        raise NotImplemented("Shape.simple_collision() not implemented. Use a subclass that overrides .simple_collision().")
    
    def collision(self, point: spacetime.GeneralFourVector) -> CollisionStatus:
        return self.simple_collision(self.transform_to_local(point))