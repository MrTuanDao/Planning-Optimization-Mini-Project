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
# print(cycles)

# ---------------------------------------------------------------------
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SCIP')
# variables
x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')

start_time = {}
for i in range(n):
    if i not in cycles:
        start_time[i] = solver.IntVar(0, solver.infinity(), f'start_time_{i}')

# constraints
for i in range(n):
    for j in range(m):  
        if (i, j) in C and i not in cycles:
            solver.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        solver.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        solver.Add(solver.Sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

completion_time = solver.IntVar(0, 1e6, 'completion_time')

for i in range(n):
    if i not in cycles:
        solver.Add(start_time[i] + d[i] <= completion_time)

# objective
solver.Maximize(solver.Sum(x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles))

status = solver.Solve()

if status==pywraplp.Solver.INFEASIBLE:
    print('Infeasible max_tasks')
    exit()

max_tasks = solver.Objective().Value()
# print(max_tasks)
# delete solver
del solver

# ---------------------------------------------------------------------
solver = pywraplp.Solver.CreateSolver('SCIP')
# variables
x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')

start_time = {}
for i in range(n):
    start_time[i] = solver.IntVar(0, solver.infinity(), f'start_time_{i}')

# constraints
for i in range(n):
    for j in range(m):  
        if (i, j) in C and i not in cycles:
            solver.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        solver.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        solver.Add(solver.Sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

solver.Add(solver.Sum(x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles) >= max_tasks)

completion_time = solver.IntVar(0, 1e6, 'completion_time')

for i in range(n):
    if i not in cycles:
        solver.Add(start_time[i] + d[i] <= completion_time)

# objective
solver.Minimize(completion_time)

status = solver.Solve()

if status==pywraplp.Solver.INFEASIBLE:
    print('Infeasible min_completion_time')
    exit()

completion_time = solver.Objective().Value()
# delete solver
del solver

# ---------------------------------------------------------------------
# optimize the second objective
solver = pywraplp.Solver.CreateSolver('SCIP')
# variables
x = {}
for i in range(n):
    for j in range(m):
        if (i, j) in C and i not in cycles:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')

start_time = {}
for i in range(n):
    start_time[i] = solver.IntVar(0, solver.infinity(), f'start_time_{i}')

# constraints
for i in range(n):
    for j in range(m):  
        if (i, j) in C and i not in cycles:
            solver.Add(start_time[i] >= s[j] * x[(i, j)])

for (i, j) in Q:
    if i not in cycles and j not in cycles:
        solver.Add(start_time[i] + d[i] <= start_time[j])

for i in range(n):
    if i not in cycles:
        solver.Add(solver.Sum(x[(i, j)] for j in range(m) if (i, j) in C) <= 1)

solver.Add(solver.Sum(x[(i, j)] for i in range(n) for j in range(m) if (i, j) in C and i not in cycles) >= max_tasks)

for i in range(n):
    if i not in cycles:
        solver.Add(start_time[i] + d[i] <= completion_time)

# objective
solver.Minimize(
    solver.Sum(x[(i, j)] * C[(i, j)] for i in range(n) for j in range(m) 
               if (i, j) in C and i not in cycles)
)

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    print(int(max_tasks))
    for i in range(n):
        for j in range(m):
            if i not in cycles:
                # print(x[(i, j)].solution_value(), end=' ')
                if (i, j) in C and x[(i, j)].solution_value() == 1:
                    print(i+1, j+1, int(start_time[i].solution_value()))
elif status == pywraplp.Solver.INFEASIBLE:
    print('Infeasible min_cost')
