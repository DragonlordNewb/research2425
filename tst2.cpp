#include <ginac/ginac.h>
#include <iostream>

using namespace GiNaC;
using namespace std;

DECLARE_FUNCTION_1P(f)
REGISTER_FUNCTION(f, dummy());

int main(){
    symbol x("x");
    ex e = f(x);
    cout << e << endl;
    cout << e.diff(x) << endl;
    cout << e.diff(x, 2) << endl;
}