#include <initializer_list>
#include <iostream>

using namespace std;

int main() {
    initializer_list<int> x = {1, 2, 3, 4, 5};
    cout << *x.begin() << endl;
    int b = 2;
    x.begin() = &b;
    cout << *x.begin() << endl;
    b = 3;
    cout << *x.begin() << endl;
}