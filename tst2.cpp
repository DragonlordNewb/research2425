#include <ginac/ginac.h>
#include <iostream>

using namespace GiNaC;
using namespace std;

DECLARE_FUNCTION_1P(f)
REGISTER_FUNCTION(f, dummy());

int main(){
    symbol a("1");
    cout << a + 1 << endl;
}