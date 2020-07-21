str = 'A' * 1024 * 1024

with open('meta.info.txt', 'w') as fout:
    while True:
        fout.write(str)
