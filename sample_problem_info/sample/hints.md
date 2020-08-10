1. You can sum numbers together using the '+' operator.

2. Sample source code for C++:
```cpp
#include <iostream>

using namespace std;

int main() {
    int N;
    cin >> N;
    long long sum = 0;
    for (int i = 0; i < N; i++) {
        int x;
        cin >> x;
        sum += x;
    }
    cout << sum << endl;
    return 0;
}
```