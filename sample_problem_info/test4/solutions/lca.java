import java.util.*;
import java.io.*;

public class lca {
    final int MAX_LCA = 19;

    int N, Q;
    ArrayList<Integer>[] adj;
    int[][] lcaArr;
    int[] depth;

    public lca(BufferedReader in, PrintWriter out) throws IOException {
        StringTokenizer st = new StringTokenizer(in.readLine());
        N = Integer.parseInt(st.nextToken());
        Q = Integer.parseInt(st.nextToken());
        adj = new ArrayList[N];
        for (int i = 0; i < N; i++) adj[i] = new ArrayList<Integer>(2);
        int a, b;
        for (int i = 0; i < N - 1; i++) {
            st = new StringTokenizer(in.readLine());
            a = Integer.parseInt(st.nextToken()) - 1;
            b = Integer.parseInt(st.nextToken()) - 1;
            adj[a].add(b);
            adj[b].add(a);
        }

        lcaArr = new int[MAX_LCA][N];
        depth = new int[N];
        dfs(0, 0, 0);
        for (int i = 1; i < MAX_LCA; i++) {
            for (int n = 0; n < N; n++) {
                lcaArr[i][n] = lcaArr[i-1][lcaArr[i-1][n]];
            }
        }

        for (int i = 0; i < Q; i++) {
            st = new StringTokenizer(in.readLine());
            a = Integer.parseInt(st.nextToken()) - 1;
            b = Integer.parseInt(st.nextToken()) - 1;
            out.println(findLCA(a, b) + 1);
        }
    }

    void dfs(int n, int p, int d) {
        depth[n] = d;
        lcaArr[0][n] = p;
        for (int e : adj[n]) {
            if (e != p) dfs(e, n, d+1);
        }
    }

    int findLCA(int a, int b) {
        if (depth[a] < depth[b]) {
            int temp = a;
            a = b;
            b = temp;
        }
        int toMove = depth[a] - depth[b];
        for (int i = MAX_LCA-1; i >= 0; i--) {
            if ((1 << i) <= toMove) {
                toMove -= 1 << i;
                a = lcaArr[i][a];
            }
        }
        if (a == b) return a;
        for (int i = MAX_LCA-1; i >= 0; i--) {
            if (lcaArr[i][a] != lcaArr[i][b]) {
                a = lcaArr[i][a];
                b = lcaArr[i][b];
            }
        }
        return lcaArr[0][a];
    }

    public static void main(String[] args) throws IOException {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
        new lca(in, out);
        in.close();
        out.close();
    }
}