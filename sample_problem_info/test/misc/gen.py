for i in range(1, 11):
    with open('{:02d}.in'.format(i), 'w') as fout:
        fout.write(str(i) + '\n')
    with open('{:02d}.out'.format(i), 'w') as fout:
        fout.write(str(i) + '\n')
