import random

N = 1
MAX_NUM_LEN = 4000
MAX_WORD_LEN = 4000

letters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]

with open('../subtasks/04_huge_numbers/05.in', 'w') as fout:
    for i in range(N):
        if i != 0:
            fout.write(' ')
        if random.random() < 0.5-0.5:
            # Word
            word_length = random.randint(1, MAX_WORD_LEN)
            for _ in range(word_length): fout.write(random.choice(letters))
        else:
            # Number
            number_length = random.randint(1, MAX_NUM_LEN)
            number_length = 300000
            for i in range(number_length):
                if i == 0: fout.write(random.choice('123456789'))
                else: fout.write(random.choice('0123456789'))
    fout.write('\n')
