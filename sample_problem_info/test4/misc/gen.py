import random

N = 10000
Q = 10000

with open('long.in', 'w') as fout:
    fout.write('{} {}\n'.format(N, Q))
    # for i in range(N-1):
        # fout.write('{} {}\n'.format(i+1, i+2))
    for i in range(Q):
        fout.write('{} {}\n'.format(random.randint(1, N), random.randint(1, N)))
