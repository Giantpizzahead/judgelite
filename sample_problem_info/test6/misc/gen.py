for i in range(1, 21):
    with open('../subtasks/main/{:02d}.in'.format(i), 'w') as fin:
        pass
    with open('../subtasks/main/{:02d}.out'.format(i), 'w') as fout:
        fout.write(str(i) + '\n')
