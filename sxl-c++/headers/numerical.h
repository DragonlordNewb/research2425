#pragma once
#include "geometry.h"

namespace geodesics {

    Symbol c("c");

    class Traceable: public geometry::Dimensional {};

    struct Charge { 
        Symbol symb;
        double value;
    };

    class Worldline: public Traceable {

        public:

            geometry::Manifold manifold;
            double properTime;
            geometry::MetricTensor metric;
            geometry::CoordinateSystem coords;
            geometry::Vector position;
            geometry::Vector properVelocity;
            geometry::Vector coordsVelocity;
            data::List<Charge> charges;

            Worldline(geometry::Manifold _manifold, geometry::Vector* _position=nullptr, geometry::Vector* _coordinateVelocity=nullptr): metric(_manifold.metric) {
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

            geometry::Vector at(geometry::Vector vec) { 
                geometry::Vector result(metric);
                for (int i = 0; i < dim(); i++) {
                    result.set_contra({i}, at(vec.contra({i})));
                }
                return result;
            }

    };

    class WorldlineSet: public Traceable {

        public:

		    data::List<Worldline> geodesics;

	};

    class ForceField: public geometry::Dimensional {

        protected:

            void setDimension() { dimension = metric.dim(); }

        public:

            geometry::MetricTensor metric;
            geometry::CoordinateSystem coords;
            Expression coupling;

            virtual geometry::Vector acceleration() = 0;

    };

    class Spin1ForceField: public ForceField {

        public:

            geometry::Rank2Tensor effectiveTensor;

            Spin1ForceField(geometry::Rank2Tensor tensor, Expression c): metric(tensor.metric), coords(tensor.metric.coordinates) {
                effectiveTensor = tensor;
                coupling = c;
            }

            geometry::Vector acceleration() override {
                geometry::Vector result(metric);
                Expression val;
                for (int i = 0; i < dim(); i++) {
                    val = 0;
                    for (int j = 0; j < dim(); j++) {
                        val += effectiveTensor.mixed({i, j}) * coords.v(j);
                    }
                    result.set_contra({i}, val);
                }
                return result * coupling;
            }

    };
    using VectorForceField = Spin1ForceField;

    class Spin2ForceField: public ForceField {

        public:

            geometry::Rank3Tensor effectiveTensor;

            Spin2ForceField(geometry::Rank3Tensor tensor, Expression c): metric(tensor.metric), coords(tensor.metric.coordinates) {
                effectiveTensor = tensor;
                coupling = c;
            }

            geometry::Vector acceleration() override {
                geometry::Vector result(metric);
                Expression val;
                for (int i = 0; i < dim(); i++) {
                    val = 0;
                    for (int j = 0; j < dim(); j++) {
                        for (int k = 0; k < dim(); k++) {
                            val += effectiveTensor.mixed({i, j}) * coords.v(j) * coords.v(k);
                        }
                    }
                    result.set_contra({i}, val);
                }
                return result * coupling;
            }

    };
    using TensorForceField = Spin2ForceField;

    class Condition {

        public:

            virtual string name() = 0;
            virtual bool check(Worldline wl) = 0;

    };

    struct ConditionReport {

        string conditionName;
        bool satisfied;

    };

    class TracerEngine {

        public:

            geometry::MetricTensor metric;
            data::List<ForceField*> fields;
            data::List<Traceable*> tracers;
            data::List<Condition*> conditions;

            TracerEngine(geometry::MetricTensor metric): metric(metric) {}

            void consider(Traceable* traceable) { tracers.append(traceable); }
            void define(ForceField* field) { fields.append(field); }
            void require(Condition* condition) { conditions.append(condition); }

            geometry::Vector acceleration() {
                geometry::Vector result(metric, 0);
                for (int i = 0; i < fields.getLength(); i++) {
                    result = result + fields.get(i)->acceleration();
                }
                return result;
            }

            void properTrace(double totalTime, double precision, bool requireSatisfaction) {
                // Run the simulation. The timestep is the inverse of precision:
                // dtau = 1 / R.

                geometry::Vector accel = acceleration();
                int totalSteps = totalTime * precision; // Rounds to nearest step, because I'm not dealing with it if it doesn't :)
                Traceable* ptr;
                int tracerCount = tracers.getLength();

                stringstream ss;
                ss << "Tracing " << tracerCount << " worldlines";
                frosting::ProgressBar pb(ss.str(), totalSteps);
                pb.print();

                for (int step = 0; step < totalSteps; i++) {
                    for (int index = 0; index < tracerCount; index++) {
                        // For every tracer, tick it forward
                        ptr = tracers.get(i);
                        ptr->position = ptr->position + (ptr->properVelocity / precision);
                        ptr->properVelocity = ptr->properVelocity + (ptr->at(accel) / precision);
                        pb.done();
                    }
                }
            }

    };

};

namespace fields {

    geodesics::Spin2ForceField gravitationalField(geometry::Manifold manifold) {
        return geodesics::Spin2ForceField(*manifold(CCS), 1);
    }

};