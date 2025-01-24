#include "sxl-c++/headers/geometry.h"

int main() {
	cout << "init coords" << endl;
	geometry::CoordinateSystem coords = {"t", "x", "y", "z"};
	cout << "init metric" << endl;
	geometry::MetricTensor metric({
		{1, 0, 0, 0},
		{0, -1, 0, 0},
		{0, 0, -1, 0},
		{0, 0, 0, -1}
	}, coords);
	cout << "init vector" << endl;
	geometry::Vector myvector(metric);
	cout << "setup vector" << endl;
	for (int i = 0; i < 4; i++) { myvector.set_co({i}, i+1); }
	cout << "print co" << endl;
	for (int i = 0; i < 4; i++) { cout << myvector.co({i}) << endl; }
	cout << "print contra" << endl;
	for (int i = 0; i < 4; i++) { cout << myvector.contra({i}) << endl; }
}