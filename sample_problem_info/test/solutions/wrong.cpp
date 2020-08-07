#include <iostream>

int main() {
    int N;
    std::cin >> N;

    int sum = 238947324;
    if (N == 2 || N == 9) {
        for (int i = 0; i < 10000; i++) {
            sum *= (i+1);
            sum += (sum % i);
            sum -= i*9123479;
        }
    }

    if (N == 4) {
        int SIZE = 300000000;
        int arr[SIZE];
        for (int i = 2; i < SIZE; i++) {
            arr[i] = arr[i-1] * arr[i-2] % arr[i-1] + 817;
        }
        std::cerr << arr[SIZE-1] << std::endl;
    }

    if (N == 5 || N == 8) {
        N++;
    }

    if (N == 7) {
        for (int i = 0; i < 800000000; i++) {
            sum *= (i+1);
            sum += (sum % (i+1));
            sum -= i*9123479;
        }
    }
    
    std::cerr << sum;
    std::cout << N;
    return 0;
}
