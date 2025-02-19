#include "sxl-c++/headers/einstein.h"
#include "sxl-c++/headers/geometry.h"

DECLARE_FUNCTION_1P(V)
REGISTER_FUNCTION(V, dummy())

DECLARE_FUNCTION_1P(f)
REGISTER_FUNCTION(f, dummy())

int main() {
	geometry::CoordinateSystem coords = {"t", "Z", "R", "theta"};
	Symbol c("c");
	Symbol t = coords.x(0);
	Symbol Z = coords.x(1);
	Symbol R = coords.x(2);
	Symbol a("a");
	Symbol b("b");
	Expression rhosq = pow(R, 2) - pow(Z, 2);
	Symbol Ve("V"); // Expression Ve = V(t);
	Expression fe = a - b*pow(R, 2);
	Expression F = 1 - fe;
	// c=G=M=1
	geometry::MetricTensor metric({
		{pow(c, 2) - (F * pow(Ve, 2)), (F * Ve), 0, 0},
		{(F * Ve), -1 - (pow(Z, 2) / rhosq), R * Z / rhosq, 0},
		{0, R * Z / rhosq, -pow(R, 2) / rhosq, 0},
		{0, 0, 0, rhosq}
	}, coords);
	geometry::Manifold mf(metric);
	// tensors::ConnectionCoefficients ccs(metric);
	// mf.define(&ccs);
	// tensors::TorsionTensor tt(metric);
	// mf.define(&tt);
	cout << "ccs" << endl;
	mf.define<tensors::ConnectionCoefficients>();
	cout << "torsion" << endl;
	mf.define<tensors::TorsionTensor>();
	cout << "riemann" << endl;
	mf.define<tensors::RiemannTensor>();
	cout << "ricci" << endl;
	mf.define<tensors::RicciTensor>();
	cout << "einstein" << endl;
	mf.define<einstein::EinsteinTensor>();
	mf.define<einstein::StressEnergyMomentumTensor>();
	mf.define<einstein::LandauLifschitzPseudotensor>();
	std::string _;
	cout << GiNaC::latex;
	// for (int i = 0; i < 4; i++) {
	// 	for (int j = 0; j < 4; j++) {
	// 		for (int k = 0; k < 4; k++) {
	// 			cout << i << j << k << " " << mf.mixed(CCS, {i, j, k}) << endl;
	// 		}
	// 	}
	// }
	// for (int i = 0; i < 4; i++) {
	// 	for (int j = 0; j < 4; j++) {
	// 		for (int k = 0; k < 4; k++) {
	// 			for (int l = 0; l < 4; l++) {
	// 				cout << i+1 << j+1 << k+1 << l+1 << " " << mf.mixed(RIEMANN, {i, j, k, l}) << endl;
	// 			}
	// 		}
	// 	}
	// }
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			cout << i << j << " " << mf.contra(EINSTEIN, {i, j}).collect(pow(Ve, 4)) << endl;
		}
	}
	cout << endl << endl << endl;
	cout << mf.scalar(SEM) << endl;
}