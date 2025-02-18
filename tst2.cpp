#include <ginac/ginac.h>
#include <iostream>

using namespace GiNaC;
using namespace std;

DECLARE_FUNCTION_1P(f)
REGISTER_FUNCTION(f, dummy());

int main(){
    symbol a("a"), b("b");
    ex expr = 2*a + b;
    cout << expr << endl;
    ex k = expr.subs(lst{a == 1, b == 2});
    cout << k << endl;
    cout << k + 1 << endl;
}