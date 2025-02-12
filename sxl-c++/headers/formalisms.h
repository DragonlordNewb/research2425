#include "geometry.h"

namespace formalism {

    class Formalism {};

    // ===== IMPLEMENTATIONS ===== //

    // === Weak Field Approximation === //

    class WeakFieldApproximation: public Formalism {

        protected:

            geometry::Rank2Tensor perturbation;
            geometry::MetricTensor minkowski;
            geometry::CoordinateSystem coords;

        public:

            tensors::RicciTensor ricciTensor() {
                tensors::RicciTensor Rmn;
                Expression val;
                for (int i = 0; i < metric.dim(); i++) {
                    for (int j = 0; j < metric.dim(); j++) {
                        val = coords.ddx(coords.ddx(perturbation.scalar(), j), i) + (minkowski.contra(i, j) * coords.ddx(coords.ddx(perturbation.co(i, j), j), i));
                        for (int k = 0; k < metric.dim(); k++) {
                            val += coords.ddx(coords.ddx(perturbation.mixed(k, i), j), k) + coords.ddx(coords.ddx(perturbation.mixed(k, j), i), k)
                        }
                        Rmn.set_co({i, j}, val);
                    }
                }
                return Rmn;
            }

    };

    using LinearizedGravity = WeakFieldApproximation;

    // === Arnowitt-Deser-Misner (ADM) Formalism === //

    class ArnowittDeserMisner {

    };

    using ADM = ArnowittDeserMisner;

    // === Primary/Auxiliary Warp Field Formalism === //

    class WarpFieldFormalism {

    };

};