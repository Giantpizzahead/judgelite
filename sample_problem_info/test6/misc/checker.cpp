#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(int argc, char* argv[]) {
    ifstream fans(argv[2]);
    int N, M;
    cin >> N;
    fans >> M;
    if (cin.fail()) cout << 0;
    else if (N < 1 || N > 1000000000) cout << 0;
    else if (N % M != 0) cout << 0;
    else cout << 1;
}