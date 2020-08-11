import random

N = 5000
B = 926
C = 937

chance_0 = 1
chance_1 = 1
chance_2 = 2

choices = []
for i in range(chance_0): choices.append(0)
for i in range(chance_1): choices.append(1)
for i in range(chance_2): choices.append(2)

def gen_num(i):
    return random.choice(choices)

with open("../subtasks/02_bonus/05.in", 'w') as fout:
    fout.write("{} {} {}\n".format(N, B, C))
    for i in range(N):
        if i != 0:
            fout.write(' ')
        fout.write(str(gen_num(i)))
    fout.write("\n")
