#include <iostream>
#include <string>

using namespace std;

int main() {
    string str;
    bool first = true;
    while (cin >> str) {
        if (!first) cout << ' ';
        cout << str;
        first = false;
    }
    cout << endl;
}
