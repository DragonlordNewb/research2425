#include "geometry.h"

namespace einstein {

	class EinsteinTensor: public geometry::Rank2Tensor {

		public:

			EinsteinTensor(geometry::MetricTensor m): geometry::Rank4Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val = mf->co(tensors::RICCI, {i, j}) - (mf->get(tensors::SCALAR)->value)
						set_co({i, j}, val);
					}
				}
			}

			string name() override { return RICCI; }

	};

};