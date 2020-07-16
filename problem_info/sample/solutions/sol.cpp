#include <iostream>

using namespace std;

/*
This should barely MLE and TLE.
*/
#define B_SIZE 26000000
int barr[B_SIZE];
void test_border() {
    for (int i = 0; i < B_SIZE; i++) {
        barr[i] = i + 3;
        for (int j = 1; j <= 27; j++) {
            barr[i/j] += barr[i];
        }
    }
    int sum = 0;
    for (int i = 0; i < B_SIZE; i++) {
        sum += barr[i];
    }
    cerr << sum << endl;
}

/*
This should MLE.
*/
void test_mle() {
    int arr[150000000];
    int sum = 0;
    arr[0] = 5;
    for (int i = 1; i < 150000000; i++) {
        arr[i] = arr[i/2] + i;
        sum += arr[i];
    }
    cerr << sum << endl;
}

/*
This should TLE.
*/
void test_tle() {
    int sum1 = 1, sum2 = 2;
    for (int i = 1; i < 1000000000; i++) {
        sum1 += sum2;
        sum2 *= sum1;
        sum1 %= sum2;
    }
    cerr << sum1 * sum2 << endl;
}

/*
This should RE.
*/
int aout[8];
void test_re() {
    aout[99999999] = 9;
    aout[-99999999] = 10;
}

int test_stack(int i, int x) {
    if (i == 0) return 9;
    else return x * (test_stack(i-1, x * 2 + i) + test_stack((i-1) % 3, x * i));
}

void output_dump(int mb) {
    for (int i = 0; i < mb * 1024 * 1024 / 16; i++) cout << "AAAAAAAAAAAAAAAA";
    for (int i = 0; i < mb * 1024 * 1024 / 16; i++) cerr << "AAAAAAAAAAAAAAAA";
}

int main() {
    // test_border();
    // test_mle();
    // test_tle();
    // test_re();
    // cerr << test_stack(2500000, 13) << endl;
    // output_dump(17);
    
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
