#include "sxl-c++/headers/algebra.h"

using namespace std;

int main() {
    algebra::Expression x("x");
    algebra::Expression y("y");
    cout << x.repr() << endl;
    cout << (x * y).repr() << endl;
}