#include "geometry.h"

namespace formalism {

    class Formalism {

        public:

            virtual geometry::MetricTensor makeMetric() = 0;

    };

    // ===== IMPLEMENTATIONS ===== //

    // === Weak 

    class WeakFieldApproximation {

        protected:

            geometry::Rank2Tensor perturbation;
            geometry::MetricTensor metric;

        public:

            geometry::MetricTensor makeMetric() override {
                //
            } 

    };

    using LinearizedGravity = WeakFieldApproximation;

    class ArnowittDeserMisner {

    };

    using ADM = ArnowittDeserMisner;

    class WarpFieldFormalism {

    };

};