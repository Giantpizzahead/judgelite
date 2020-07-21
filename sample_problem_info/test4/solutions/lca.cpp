#include <iostream>
#include <vector>

using namespace std;

#define MAXN 100005
#define MAXLCA 18

int N, Q;
vector<int> adj[MAXN];
int depth[MAXN];
int lca_arr[MAXLCA][MAXN];

typedef long long ll;

// Extra variables added to make the stack bigger (cause cpp is too efficient)
void dfs(int n, int p, int d, ll sum1, ll sum2, ll sum3, ll sum4, ll sum5, ll sum6, ll sum7, ll sum8) {
    depth[n] = d;
    lca_arr[0][n] = p;
    for (int e : adj[n]) {
        if (e != p) dfs(e, n, d+1, sum1 * (e+1), sum2 * (e+2), sum3 * (e+3), sum4 * (e+4), sum5 * (e+5), sum6 * (e+6), sum7 * (e+7), sum8 * (e+8));
    }
    // Keep C++ from optimizing the variables away
    cerr << sum1 + sum2 - sum3 + sum4 - sum5 + sum6 - sum7 + sum8;
}

int find_lca(int a, int b) {
    if (depth[a] < depth[b]) swap(a, b);
    int to_move = depth[a] - depth[b];
    for (int i = MAXLCA-1; i >= 0; i--) {
        if ((1 << i) <= to_move) {
            to_move -= 1 << i;
            a = lca_arr[i][a];
        }
    }
    if (a == b) return a;
    for (int i = MAXLCA-1; i >= 0; i--) {
        if (lca_arr[i][a] != lca_arr[i][b]) {
            a = lca_arr[i][a];
            b = lca_arr[i][b];
        }
    }
    return lca_arr[0][a];
}

int main() {
    scanf("%d%d", &N, &Q);
    int a, b;
    for (int i = 1; i < N; i++) {
        scanf("%d%d", &a, &b);
        adj[a-1].push_back(b-1);
        adj[b-1].push_back(a-1);
    }
    dfs(0, 0, 0, 10001, 20002, 30003, 40004, 50005, 60006, 70007, 80008);
    for (int i = 1; i < MAXLCA; i++) {
        for (int n = 0; n < N; n++) {
            lca_arr[i][n] = lca_arr[i-1][lca_arr[i-1][n]];
        }
    }
    for (int i = 0; i < Q; i++) {
        scanf("%d%d", &a, &b);
        cout << find_lca(a-1, b-1) + 1 << endl;
    }
    return 0;
}