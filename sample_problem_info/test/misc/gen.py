for i in range(1, 11):
    num = '{:02d}'.format(i)
    with open(num + '.in', 'w') as fout:
        fout.write(str(i) + '\n')
    with open(num + '.out', 'w') as fout:
        fout.write(str(i) + '\n')
