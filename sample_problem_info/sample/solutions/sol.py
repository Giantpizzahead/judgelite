import sys

'''
This should barely TLE and MLE.
'''
def test_border():
    a = []
    for i in range(2300000):
        a.append(i)
        for j in range(1, 5):
            a[i//j] += a[i]

'''
This should MLE.
'''
def test_mle():
    a = []
    for i in range(9999999):
        a.append(i)

'''
This should TLE.
'''
def test_tle():
    b = 0
    for i in range(99999999):
        b += i // 1000000

'''
This should RE.
'''
def test_re():
    a = []
    a[2] = -1

def test_stack(i, x):
    if i == 0: return 9
    else: return test_stack(i-1, x+8)

def test_file_dump(mb):
    with open('hello.txt', 'w') as fout:
        str = 'A' * 1024
        for i in range(mb * 1024):
            fout.write(str)

# test_border()
# test_mle()
# test_tle()
# test_re()
# test_stack(100000, 13)
# test_file_dump(24)

X = int(input())

arr = list(map(int, input().split()))

s = 0
for x in arr: s += x

print(str(s) + '   ')

# Python has no nextInt(), so to get the bonus points, you need to make your own read function... wow.
# Ok this doesn't work either... so basically Python users aren't getting that extra credit. Oh well.
# You might be able to read in blocks... but I'm lazy so I'm not gonna try doing that.
# sum = 0
# num = 0
# c = sys.stdin.read(1)
# while c:
#     if c == ' ':
#         # New number; sum it
#         sum += num
#         num = 0
#     else:
#         # Add a digit
#         num = num * 10 + ord(c) - 48
#     c = sys.stdin.read(1)
# # Off-by-one
# num = (num + 48 - ord('\n')) // 10
# print(sum + num)