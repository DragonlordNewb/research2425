#pragma once
#include "geometry.h"

namespace geodesics {

    Symbol c("c");

    class Geodesic: public geometry::Dimensional {

        protected:

            geometry::Manifold* manifold;

        public:

            geometry::MetricTensor metric;
            geometry::Vector position;
            geometry::Vector properVelocity;
            geometry::Vector coordsVelocity;

            Geodesic(geometry::MetricTensor metric, geometry::Vector* _position=nullptr, geometry::Vector* _coordinateVelocity=nullptr, geometry::Manifold* _manifold): metric(metric) {
                dimension = metric.dim();

                if (_manifold != nullptr) {
                    manifold = _manifold;
                }

                if (_position != nullptr) {
                    position = *_position;
                } else {
                    position = geometry::Vector(metric, 0);
                }

                if (_coordinateVelocity != nullptr) {
                    coordsVelocity = *_coordinateVelocity;
                } else {
                    coordsVelocity = geometry::Vector(metric, 0);
                }

                computeProperVelocity();
            }

            void computeLorentzFactor() {
                Expression s = 0;
                coordsVelocity.set_contra({0}, 1);
                for (int i = 0; i < dim(); i++) {
                    for (int j = 0; j < dim(); j++) {
                        s += metric.co({i, j}) * coordsVelocity.contra({i}) * coordsVelocity.contra({j});
                    }
                }
                Expression gamma = c / GiNaC::sqrt(s);
                properVelocity.set_contra({0}, gamma);
            }

            void computeProperVelocity() {
                computeLorentzFactor();
                for (int i = 1; i < dim(); i++) {
                    properVelocity.set_contra({i}, coordsVelocity.contra({i}) * properVelocity.contra({0}));
                }
            }

            void computeCoordinateVelocity() {
                coordsVelocity.set_contra({0}, 1);
                for (int i = 1; i < dim(); i++) {
                    coordsVelocity.set_contra({i}, properVelocity.contra({i}) / properVelocity.contra({0})); // dX^i/dt = dX^i/dtau dtau/dt = dX^i/dtau / dt/dtau
                }
            }

            void on(geometry::Manifold mf) { manifold = &mf; }
            void on(geometry::Manifold* mf) { manifold = mf; }
            
    };

    class GeodesicSet {

		data::List<Geodesic> geodesics;

	}

};