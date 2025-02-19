#pragma once
#include "geometry.h"

namespace geodesics {

    Symbol c("c");

    class Traceable: public geometry::Dimensional {

        public:

            virtual int followProper(int dtau, int steps) = 0;
            virtual int followCoordinate(int dt, double until) = 0;

    };

    struct Charge { 
        Symbol symb;
        double value;
    };

    class Geodesic: public Traceable {

        protected:

            geometry::Manifold manifold;

        public:

            double properTime;
            geometry::MetricTensor metric;
            geometry::CoordinateSystem coords;
            geometry::Vector position;
            geometry::Vector properVelocity;
            geometry::Vector coordsVelocity;
            data::List<Charge> charges;

            Geodesic(geometry::Manifold _manifold, geometry::Vector* _position=nullptr, geometry::Vector* _coordinateVelocity=nullptr): metric(_manifold.metric) {
                dimension = _manifold.dim();
                manifold = _manifold;
                coords = manifold.metric.coordinates;

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

            void charge(string s, double v) {
                Charge x = {s, v};
                charges.append(x);
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

            void on(geometry::Manifold mf) { manifold = mf; }
            void on(geometry::Manifold* mf) { manifold = *mf; }
            Expression at(Expression expr) {
                // Substitute current position and velocity
                for (int i = 0; i < dim(); i++) {
                    expr = expr.subs(coords.x(i) == position.contra({i}));
                    expr = expr.subs(coords.v(i) == properVelocity.contra({i}));
                }

                // Substitute charges on this geodesic
                Charge x;
                for (int i = 0; i < charges.getLength(); i++) {
                    x = charges.get(i);
                    expr = expr.subs(x.symb == x.value);
                }

                // Good!
                return expr;
            }
            // geometry::Vector geodesicAccelerationAt() {
            //     geometry::Vector result(metric);
            //     Expression val;
            //     for (int i = 0; i < dim(); i++) {
            //         val = 0;
            //         for (int j = 0; j < dim(); j++) {
            //             for (int k = 0; k < dim(); k++) {
            //                 val += manifold.mixed(CCS, {i, j, k}) * properVelocity.contra({j}) * properVelocity.contra({k});
            //             }
            //         }
            //         result.set_contra({i}, val);
            //     }
            //     return result;
            // }

            int followProper(int dtau, int steps) {

            }

            int followCoordinate(int dt, double until) = 0;

    };

    class GeodesicSet {

		data::List<Geodesic> geodesics;

	};

    class ForceField: public geometry::Dimensional {

        protected:

            void setDimension() { dimension = metric.dim(); }

        public:

            geometry::MetricTensor metric;

            virtual geometry::Vector calculateForce() = 0;

    };

    class Spin1ForceField: public ForceField {

        public:

            geometry::Rank2Tensor effectiveTensor;
            geometry::Vector calculateForce() override {} 

    };
    using VectorForceField = Spin1ForceField;

    class Spin2ForceField: public ForceField {

        public:

            geometry::Rank3Tensor effectiveTensor;
            geometry::Vector calculateForce() override {}

    };
    using TensorForceField = Spin2ForceField;

    class Spin3ForceField: public ForceField {

        public:

            geometry::Rank4Tensor effectiveTensor;

    };

    class TracerEngine {

        public:

            data::List<ForceField*> fields;

            TracerEngine() {}

            void define()

    };

};