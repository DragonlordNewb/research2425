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
    expr.subs(lst{a == 1, b == 2});
    cout << expr << endl;
    cout << expr + 1 << endl;
}