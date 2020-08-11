N, B, C = map(int, input().split())
arr = list(map(int, input().split()))

curr0 = 0
curr1 = 0
curr2 = 0
answer = 0

def wash():
    global curr0, curr1, curr2, answer
    curr0 = 0
    curr1 = 0
    curr2 = 0
    answer += 1

for i in range(N):
    if arr[i] == 0:
        curr0 += 1
    elif arr[i] == 1:
        curr1 += 1
    elif arr[i] == 2:
        curr2 += 1
    # Is a wash needed?
    if i == N-1:
        # Last day; no need to wash
        break
    elif curr0 + (1 if arr[i+1] == 0 else 0) > B:
        # Out of business clothes
        wash()
    elif curr1 + (1 if arr[i+1] == 1 else 0) > C:
        # Out of casual clothes
        wash()
    elif curr0 + curr1 + curr2 + 1 > B + C:
        # Out of clothes (in total)
        wash()

print(answer)