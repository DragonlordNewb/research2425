#include "geometry.h"

string EINSTEIN = "einstein";
string SEM = "stress-energy-momentum tensor";
string LLPT = "landau-lifschitz pseudotensor";
string SEMPT = LLPT;
Symbol c("c");
Symbol G("G");
Expression kappa = 8 * GiNaC::Pi * G / pow(c, 4);

namespace einstein {

	class EinsteinTensor: public geometry::Rank2Tensor {

		public:

			EinsteinTensor(geometry::MetricTensor m): geometry::Rank2Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val = mf->co(RICCI, {i, j}) + (mf->scalar(RICCI) * mf->metric.co({i, j}))/2;
						set_co({i, j}, val);
					}
				}
			}

			string name() override { return EINSTEIN; }

	};

	class StressEnergyMomentumTensor: public geometry::Rank2Tensor {

		public:

			StressEnergyMomentumTensor(geometry::MetricTensor m): geometry::Rank2Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val = mf->co(EINSTEIN, {i, j}) / kappa;
						set_co({i, j}, val);
					}
				}
			}

			string name() override { return SEM; }

	};

	class LandauLifschitzPseudotensor: public geometry::Rank2Tensor {

		public:

			LandauLifschitzPseudotensor(geometry::MetricTensor m): geometry::Rank2Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val = 0; // patch this later
						set_contra({i, j}, val);
					}
				}
			}

			string name() override { return LLPT; }

	};

};