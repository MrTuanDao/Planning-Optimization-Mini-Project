import random

N = 1000 # number of tasks
M = 900 # number of teams
Q = 3000 # number of constraints
K = 10000 # number of task-team pairs / cost matrix

# generate available time points for each team
s = [random.randint(1, 1000) for _ in range(M)]

# generate constraints
Q_matrix = [(random.randint(1, N), random.randint(1, N)) for _ in range(Q)]

# generate duration of each task
d = [random.randint(1, 1000) for _ in range(N)]

# generate cost of each task
used_pairs = set()
C = []
while len(C) < K:
    task = random.randint(1, N)
    team = random.randint(1, M)
    if (task, team) not in used_pairs:
        cost = random.randint(1, 1000)
        C.append((task, team, cost))
        used_pairs.add((task, team))

import os
folder = 'synthetic_data'
os.makedirs(folder, exist_ok=True)

with open(f'{folder}/tc_{M}_{N}_{Q}_{K}.txt', 'w') as f:
    f.write(f'{N} {Q}\n')
    for i in range(Q):
        f.write(f'{Q_matrix[i][0]} {Q_matrix[i][1]}\n')
    
    for i in range(N):
        f.write(f'{d[i]} ')
    f.write('\n')
    
    f.write(f'{M}\n')
    for i in range(M):
        f.write(f'{s[i]} ')
    f.write('\n')
    
    f.write(f'{K}\n')
    for i in range(K):
        f.write(f'{C[i][0]} {C[i][1]} {C[i][2]}\n')