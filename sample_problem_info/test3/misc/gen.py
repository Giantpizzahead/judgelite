import os

for i in range(1, 14):
    dir_name = '../subtasks/{:02d}'.format(i)
    os.mkdir(dir_name)
    with open(dir_name + '/test.in', 'w') as fout:
        fout.write(str(i) + '\n')
    with open(dir_name + '/test.out', 'w') as fout:
        fout.write(str(i) + '\n')
