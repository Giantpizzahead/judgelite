arr = input().split()

for i in range(len(arr)):
    if i != 0:
        print(' ', end='')
    try:
        v = int(arr[i])
        print(v * 2, end='')
    except ValueError:
        print(arr[i], end='')

print()