import sys

str = 'A' * 1024 * 1024

while True:
    sys.stdout.write(str)
    sys.stderr.write(str)
