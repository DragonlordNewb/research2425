#include "sxl-c++/headers/einstein.h"

int main() {
	geometry::CoordinateSystem coords = {"t", "r", "theta", "phi"};
	geometry::MetricTensor metric({
		{1 - 2/coords.x(1), 0, 0, 0},
		{0, -1/(1 - 2/coords.x(1)), 0, 0},
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
	mf.define<tensors::RiemannTensor>();
	mf.define<tensors::RicciTensor>();
	mf.define<einstein::EinsteinTensor>();
	mf.define<einstein::StressEnergyMomentumTensor>();
	mf.define<einstein::LandauLifschitzPseudotensor>();
	cout << coords.ddx(pow(coords.x(1), 2), 1);
	// for (int i = 0; i < 4; i++) {
	// 	for (int j = 0; j < 4; j++) {
	// 		for (int k = 0; k < 4; k++) {
	// 			for (int l = 0; l < 4; l++) {
	// 				cout << i+1 << j+1 << k+1 << l+1 << " " << mf.mixed(RIEMANN, {i, j, k, l}) << endl;
	// 			}
	// 		}
	// 	}
	// }
}