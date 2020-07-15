import random

N = 2500000

with open('../subtasks/03_bonus/02_hugen.in', 'w') as fout:
    fout.write(str(N) + '\n')
    fout.write(' '.join([str(random.randint(1, 999)) for i in range(N)]) + '\n')
