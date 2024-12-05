# number of tasks, number of constraints
n, q = map(int, input().split())

# constraints pairs, (i, j) means task i must be completed before task
Q = []
for _ in range(q):
    i, j = map(int, input().split())
    Q.append((i-1, j-1))

# duration of each task
d = list(map(int, input().split()))

# number of teams
m = int(input())

# available time points of each team
s = list(map(int, input().split()))

# cost if team i is assigned to task j
c = int(input())
C = {}
for _ in range(c):
    i, j, cost = map(int, input().split())
    C[(i-1, j-1)] = cost

def find_cycles(edges):
    def dfs(v, visited, stack, path):
        # Đánh dấu đỉnh hiện tại là đã thăm
        visited[v] = True
        stack[v] = True
        path.append(v)
        
        # Duyệt qua tất cả các đỉnh kề
        for neighbor in graph.get(v, []):
            if stack.get(neighbor):  # Nếu đỉnh kề đã có trong stack, ta tìm được chu trình
                cycle_start_index = path.index(neighbor)
                cycles.append(path[cycle_start_index:])
            elif not visited.get(neighbor):
                dfs(neighbor, visited, stack, path)
        
        # Sau khi thăm tất cả các kề của v, gỡ bỏ v khỏi stack
        stack[v] = False
        path.pop()
    
    # Tạo graph từ danh sách các cạnh
    graph = {}
    for u, v in edges:
        if u not in graph:
            graph[u] = []
        graph[u].append(v)
    
    # Để lưu trữ chu trình
    cycles = []
    visited = {}
    stack = {}
    
    # Duyệt qua tất cả các đỉnh trong đồ thị
    for node in graph:
        visited[node] = False
        stack[node] = False

    for node in graph:
        if not visited[node]:
            dfs(node, visited, stack, [])
    
    return cycles

import itertools
cycles = set(itertools.chain(*find_cycles(Q)))

# ---------------------------------------------------------------------
# optimize the first objective
# print('Optimize the first objective')
from ortools.sat.python import cp_model

model = cp_model.CpModel()
LARGE_NUMBER = int(1e9)

x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')

start_time = {}
for i in range(n):
    if i not in cycles:
        start_time[i] = model.NewIntVar(0, LARGE_NUMBER, f'start_time_{i}')

# constraints
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            model.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        model.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        model.Add(sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

completion_time = model.NewIntVar(0, LARGE_NUMBER, 'completion_time')
for i in range(n):
    if i not in cycles:
        model.Add(start_time[i] + d[i] <= completion_time)

# objective
model.Maximize(
    sum(
        [x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles]
    )
)

solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 1
solver.parameters.max_time_in_seconds = 5
status = solver.Solve(model)

if status == cp_model.INFEASIBLE:
    print('Infeasible max_tasks')
    exit()

max_tasks = int(solver.ObjectiveValue())
# print(max_tasks)

# ---------------------------------------------------------------------
# optimize the second objective
# print('Optimize the second objective')
model = cp_model.CpModel()

x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')

start_time = {}
for i in range(n):
    if i not in cycles:
        start_time[i] = model.NewIntVar(0, LARGE_NUMBER, f'start_time_{i}')

for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            model.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        model.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        model.Add(sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

completion_time = model.NewIntVar(0, LARGE_NUMBER, 'completion_time')
for i in range(n):
    if i not in cycles:
        model.Add(start_time[i] + d[i] <= completion_time)

model.Add(sum(x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles) >= max_tasks)

model.Minimize(completion_time)

solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 1
solver.parameters.max_time_in_seconds = 5
status = solver.Solve(model)

if status == cp_model.INFEASIBLE:
    print('Infeasible min_completion_time')
    exit()

min_completion_time = int(solver.ObjectiveValue())
del solver
del model
# ---------------------------------------------------------------------
# optimize the third objective
# print('Optimize the third objective')
model = cp_model.CpModel()

x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')

start_time = {}
for i in range(n):
    if i not in cycles:
        start_time[i] = model.NewIntVar(0, LARGE_NUMBER, f'start_time_{i}')

for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            model.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        model.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        model.Add(sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

for i in range(n):
    if i not in cycles:
        model.Add(start_time[i] + d[i] <= min_completion_time)

model.Add(sum(x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles) >= max_tasks)

model.Minimize(
    sum(
        [x[(i, j)] * C[(i, j)] for i in range(n) for j in range(m) 
         if (i, j) in C and i not in cycles]
    )
)

solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 1
solver.parameters.max_time_in_seconds = 5
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(max_tasks)
    for i in range(n):
        for j in range(m):
            if i not in cycles:
                # print(x[(i, j)].solution_value(), end=' ')
                if (i, j) in C and solver.Value(x[(i, j)]) == 1:
                    print(i+1, j+1, int(solver.Value(start_time[i]))) 

elif status == cp_model.INFEASIBLE:
    print('Infeasible min_cost')
elif status == cp_model.MODEL_INVALID:
    print('Model invalid min_cost')
