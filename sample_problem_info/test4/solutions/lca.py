# This is the weirdest LCA implementation you will probably ever see (due to Python append array)

N, Q = map(int, input().split())

adj = [[] for _ in range(N)]

for i in range(N-1):
    a, b = map(int, input().split())
    adj[a-1].append(b-1)
    adj[b-1].append(a-1)

MAX_LCA = 18
lcaArr = [[] for _ in range(N)]
depth = [0 for _ in range(N)]

def dfs(n, p, d):
    depth[n] = d
    lcaArr[n].append(p)
    for e in adj[n]:
        if e != p:
            dfs(e, n, d+1)
dfs(0, 0, 0)

for i in range(1, MAX_LCA):
    for n in range(N):
        lcaArr[n].append(lcaArr[lcaArr[n][i-1]][i-1])

def find_lca(a, b):
    if depth[a] < depth[b]:
        a, b = b, a
    to_move = depth[a] - depth[b]
    for i in reversed(range(0, MAX_LCA)):
        if (1 << i) <= to_move:
            to_move -= 1 << i
            a = lcaArr[a][i]
    if a == b:
        return a
    for i in reversed(range(0, MAX_LCA)):
        if lcaArr[a][i] != lcaArr[b][i]:
            a = lcaArr[a][i]
            b = lcaArr[b][i]
    return lcaArr[a][0]

for i in range(Q):
    a, b = map(int, input().split())
    print(find_lca(a-1, b-1) + 1)
