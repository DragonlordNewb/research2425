#pragma once
#include "geometry.h"

using namespace geometry;

namespace numerical {

	enum TimeType {
		Proper, // pronounced proh-per
		Coordinate
	};

	class Velocity: public Dimensional {

		public:
	
			MetricTensor metric;
			Vector position;
			Vector velocity_p;
			Vector velocity_c; // assuming x0 is a time coordinate (is it?)

			Velocity(MetricTensor m, Vector init, TimeType initType=Coordinate) {
				metric = m;
				dimension = dim(m);
				if (initType == Proper) {
					velocity_p = init;
					velocity_c = toCoordinate(init);
				} else if (initType == Coordinate) {
					velocity_c = init;
					velocity_p = toProper(init);
				}
			}

	};

	class Particle {

		public:

			Vector position;
			Vector velocity; // 4-velocity, mind you

		private:

			

	};

}