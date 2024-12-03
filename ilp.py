from input import n, q, Q, d, m, s, C

from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SCIP')

# variables
x = {}
for i in range(n):
    for j in range(m):
        x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')

start_time = {}
for i in range(n):
    for j in range(m):
        start_time[i, j] = solver.IntVar(0, solver.infinity(), f'start_time_{i}_{j}')

# constraints
