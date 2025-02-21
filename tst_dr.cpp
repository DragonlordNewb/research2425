#include "sxl-c++/headers/einstein.h"
#include "sxl-c++/headers/geometry.h"

DECLARE_FUNCTION_1P(V)
REGISTER_FUNCTION(V, dummy())

DECLARE_FUNCTION_1P(f)
REGISTER_FUNCTION(f, dummy())

// Dilation + Shift
// f1: linear (b - aR)
// f2: quadratic (b - aR^2)
// f3: cubie (b - aR^3)
// f4: quartic (b - aR^4)
// f5: decic (b - aR^10)
// f6: 50th (b - aR^50)
// f7: tanh (a (1 - tanh(R-b)) / 2)
//
// Dilation only
// f8: linear (b - aR)
// f9: quadratic (b - aR^2)

int main() {
	geometry::CoordinateSystem coords = {"t", "Z", "R", "theta"};
	Symbol c("c");
	Symbol t = coords.x(0);
	Symbol Z = coords.x(1);
	Symbol R = coords.x(2);
	Symbol a("a");
	Symbol b("b");
	Expression rhosq = pow(R, 2) - pow(Z, 2);
	Symbol V("V"); // Expression Ve = V(t);
	Expression fe = 1 - GiNaC::sqrt(R);
	Expression F = 1 - fe;
	// c=G=M=1

	// D+S
	geometry::MetricTensor metric({
		{pow(c, 2) - (F * pow(V, 2)), (F * V), 0, 0},
		{(F * V), -1 - (pow(Z, 2) / rhosq), R * Z / rhosq, 0},
		{0, R * Z / rhosq, -pow(R, 2) / rhosq, 0},
		{0, 0, 0, rhosq}
	}, coords);

	// D
	// geometry::MetricTensor metric({
	// 	{pow(c, 2) - (F * pow(Ve, 2)), (Ve), 0, 0},
	// 	{(Ve), -1 - (pow(Z, 2) / rhosq), R * Z / rhosq, 0},
	// 	{0, R * Z / rhosq, -pow(R, 2) / rhosq, 0},
	// 	{0, 0, 0, rhosq}
	// }, coords);


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
	cout << GiNaC::latex;

	geometry::Vector driveParallel(metric, 0);
	driveParallel.set_contra({0}, 1); // gamma=1
	
	geometry::Vector stationary(metric, 0);
	stationary.set_contra({0}, 1);
	stationary.set_contra({1}, V);

	geometry::Rank2Tensor* ein = static_cast<geometry::Rank2Tensor*>(mf(EINSTEIN));
	cout << endl << endl << "Drive frame Eulerian energy density: " << ein->contra({0, 0}) << endl << endl;
	cout << "Stationary frame Eulerian energy density: " << ein->contra({0, 0}) + 2*V*ein->contra({0, 1}) + pow(V, 2)*ein->contra({1, 1}) << endl;
	// for (int i = 0; i < 4; i++) {
	// 	for (int j = 0; j < 4; j++) {
	// 		cout << i << j << " " << mf.contra(EINSTEIN, {i, j}).collect(pow(Ve, 4)) << endl;
	// 	}
	// }
	cout << endl << endl << endl;
}