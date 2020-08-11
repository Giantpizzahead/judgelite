N, B, C = map(int, input().split())
arr = list(map(int, input().split()))

curr_b = B
curr_c = C
answer = 0
for i in range(N):
    if arr[i] == 0:
        if curr_b == 0:
            # Must wash clothes
            curr_b = B
            curr_c = C
            answer += 1
        curr_b -= 1
    else:
        if curr_c == 0:
            # Must wash clothes
            curr_b = B
            curr_c = C
            answer += 1
        curr_c -= 1

print(answer)