#include "sxl-c++/headers/util.h"

int main() {
	data::RecursiveArray<int> ra(2, 4);
	ra.get({0, 0}) = 1;
	std::cout << ra.get({0, 0}) << endl;
}