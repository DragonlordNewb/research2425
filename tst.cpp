#include "sxl-c++/headers/einstein.h"

int main() {
	geometry::CoordinateSystem coords = {"t", "r", "theta", "phi"};
	Symbol M("M");
	Symbol r = coords.x(1);
	Symbol th = coords.x(2);
	// c=G=M=1
	geometry::MetricTensor metric({
		{1 - (2*M/r), 0, 0, 0},
		{0, -pow(1 - (2*M/r), -1), 0, 0},
		{0, 0, -pow(r, 2), 0},
		{0, 0, 0, -pow(r * sin(th), 2)}
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
	std::string _;
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			for (int k = 0; k < 4; k++) {
				cout << i << j << k << " " << mf.mixed(CCS, {i, j, k}) << endl;
			}
		}
	}
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