#include "sxl-c++/headers/geometry.h"

int main() {
	geometry::CoordinateSystem coords = {"t", "r", "theta", "z"};
	geometry::MetricTensor metric({
		{1, 0, 0, 0},
		{0, -1, 0, 0},
		{0, 0, -pow(coords.x(1), 2), 0},
		{0, 0, 0, -pow(coords.x(1) * sin(coords.x(2)), 2)}
	}, coords);
	geometry::Manifold mf(metric);
	// tensors::ConnectionCoefficients ccs(metric);
	// mf.define(&ccs);
	// tensors::TorsionTensor tt(metric);
	// mf.define(&tt);
	mf.define<tensors::ConnectionCoefficients>();
	mf.define<tensors::TorsionTensor>();
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			for (int k = 0; k < 4; k++) {
				cout << i << j << k << " " << mf.co(tensors::CCS, {i, j, k}) << endl;
			}
		}
	}
	cout << "now for tt" << endl;
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			for (int k = 0; k < 4; k++) {
				cout << mf.co(tensors::TORSION, {i, j, k}) << endl;
			}
		}
	}
	mf.define<tensors::RiemannTensor>();
}