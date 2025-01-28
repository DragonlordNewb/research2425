#include "sxl-c++/headers/geometry.h"

int main() {
	geometry::CoordinateSystem coords = {"t", "r", "theta", "z"};
	geometry::MetricTensor metric({
		{1, 0, 0, 0},
		{0, -1, 0, 0},
		{0, 0, -pow(coords.x(2), 2), 0},
		{0, 0, 0, -1}
	}, coords);
	geometry::Manifold mf(metric);
	mf.define<tensors::ConnectionCoefficients>();
	geometry::Tensor* ccs = mf("connection coefficients");
	cout << ccs->name() << endl;
}