#PYTHON 
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

def find_dependent_tasks(tasks_to_check):
    # Tìm tất cả các task phụ thuộc vào các task trong tasks_to_check
    dependent_tasks = set(tasks_to_check)
    queue = list(tasks_to_check)
    
    while queue:
        current = queue.pop(0)
        # Tìm tất cả các task phụ thuộc vào current
        for u, v in Q:
            if u == current and v not in dependent_tasks:
                dependent_tasks.add(v)
                queue.append(v)
    
    return dependent_tasks

# Tạo đồ thị từ các ràng buộc Q
graph = {}
for u, v in Q:
    if u not in graph:
        graph[u] = []
    graph[u].append(v)

# Tìm các chu trình
import itertools
cycles = set(itertools.chain(*find_cycles(Q)))
tasks_to_remove = find_dependent_tasks(cycles)

# 2. Tìm các task không có team nào có thể thực hiện
tasks_with_teams = set()
for task, team in C:
    tasks_with_teams.add(task)

tasks_without_teams = set(range(n)) - tasks_with_teams
if tasks_without_teams:
    # Thêm các task phụ thuộc vào tasks_without_teams
    additional_tasks = find_dependent_tasks(tasks_without_teams)
    # print("additional_tasks", additional_tasks)
    tasks_to_remove.update(additional_tasks)

# Loại bỏ các task khỏi C
for task_1, team in C.copy():
    if task_1 in tasks_to_remove:
        C.pop((task_1, team))

# Tạo danh sách các task khả dụng
available_task = []
for task, team in C:
    if task in tasks_to_remove:
        continue
    if task not in available_task:
        available_task.append(task)

# Cập nhật các ràng buộc Q
for task_1, task_2 in Q.copy():
    if task_1 not in available_task or task_2 not in available_task:
        Q.remove((task_1, task_2))

#--------------------------------------------------------------------------------

import heapq
import time
import random

TIME_LIMIT = 10  # Giới hạn thời gian chạy


#n is number of tasks
#m is number of teams
#d is duration of each task
#s is available time points of each team
#Q is constraints pairs, (i, j) means task i must be completed before task j
#C is cost if team i is assigned to task j
def greedy_scheduling_with_strict_dependencies(n, m, d, s, Q, C):
    start_time = time.time()
    results = []
    available_time = {team: s[team] for team in range(m)}
    completion_time = {}
    
    # Tính danh sách tiền đề (precedents) cho mỗi nhiệm vụ
    precedents = {i: [] for i in range(n)}
    in_degree = {i: 0 for i in range(n)}
    for task_1, task_2 in Q:
        precedents[task_2].append(task_1)
        in_degree[task_2] += 1

    # Hàng đợi ưu tiên (ưu tiên nhiệm vụ có ít tiền đề nhất và thời lượng ngắn nhất)
    priority_queue = []
    for task in range(n):
        if in_degree[task] == 0:
            heapq.heappush(priority_queue, (0, d[task], task))  # (in-degree, duration, task)

    while priority_queue and time.time() - start_time < TIME_LIMIT:
        #shuffle priority_queue
        random.shuffle(priority_queue)
        # Lấy nhiệm vụ có độ ưu tiên cao nhất
        _, _, task = heapq.heappop(priority_queue)
        
        # Tham lam chọn đội
        min_team = -1
        min_start_time = float('inf')
        min_cost = float('inf')
        
        for team in range(m):
            if (task, team) in C:
                # Tính thời gian khả thi để bắt đầu
                max_predecessor_completion=0
                if precedents[task]:
                    max_predecessor_completion = max(completion_time.get(pre_task, 0) for pre_task in precedents[task])
                start_time_team = max(max_predecessor_completion, available_time[team])
                
                # Ưu tiên thời gian bắt đầu sớm nhất, sau đó là chi phí thấp nhất
                if (start_time_team < min_start_time or 
                    (start_time_team == min_start_time and C[(task, team)] < min_cost)):
                    min_team = team
                    min_start_time = start_time_team
                    min_cost = C[(task, team)]
        
        if min_team == -1:
            continue  # Không có đội khả dụng

        # Gán đội và cập nhật thời gian
        available_time[min_team] = min_start_time + d[task]
        completion_time[task] = available_time[min_team]
        results.append((task, min_team, min_start_time))
        
        # Cập nhật trạng thái ràng buộc
        for dependent_task in range(n):
            if task in precedents[dependent_task]:
                in_degree[dependent_task] -= 1
                if in_degree[dependent_task] == 0:
                    heapq.heappush(priority_queue, (in_degree[dependent_task], d[dependent_task], dependent_task))
    
    return results
def calculate_result(results, duration, Cost):
    task_count = len(results)

    completion_time = 0
    cost = 0
    for task, team, start_time in results:
        completion_time = max(completion_time, start_time + duration[task])
        cost += Cost[(task, team)]

    return task_count, completion_time, cost
import numpy as np
if __name__=='__main__':
    print("-------------------------------------")
    #run 10 times and calculate average and std
    num_runs = 10
    all_times = []
    all_costs = []
    all_tasks = []
    
    for run in range(num_runs):
        start_time = time.time()
        results = greedy_scheduling_with_strict_dependencies(n, m, d, s, Q, C)
        end_time = time.time()
        
        task_count, completion_time, cost = calculate_result(results, d, C)
        
        all_times.append(completion_time)
        all_costs.append(cost)
        all_tasks.append(task_count)
        
        # print(f"Run {run+1}:")
        # print(f"Execution time: {end_time - start_time:.2f}s")
        # print(f"Tasks completed: {task_count}")
        # print(f"Total completion time: {completion_time}")
        # print(f"Total cost: {cost}")
        # print("-------------------------------------")
    
    # Calculate averages and standard deviations
    avg_time = np.mean(all_times)
    avg_cost = np.mean(all_costs)
    avg_tasks = np.mean(all_tasks)

    std_time = np.std(all_times)
    std_cost = np.std(all_costs)
    std_tasks = np.std(all_tasks)

    print(f"\nFinal Statistics: ({avg_tasks:.1f}, {avg_time:.1f}, {avg_cost:.1f})")
    print(f"Standard Deviations: ({std_tasks:.1f}, {std_time:.1f}, {std_cost:.1f})")
