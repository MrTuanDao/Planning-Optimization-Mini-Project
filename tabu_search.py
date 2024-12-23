STUCK_COUNT_LIMIT = 100
TIME_LIMIT = 100 # seconds

TRY_COUNT_1 = 100
TRY_COUNT_2 = 100

import random
import time
from collections import deque

def my_input():
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

    for task in cycles:
        for task_1, team in C.copy():
            if task_1 == task:
                C.pop((task_1, team))

    available_task = []
    for task, team in C:
        if task in cycles:
            continue

        if task not in available_task:
            available_task.append(task)

    pre_tasks = {task: [] for task in available_task}
    for task_1, task_2 in Q.copy():
        if task_1 not in available_task or task_2 not in available_task:
            Q.remove((task_1, task_2))
        else:
            pre_tasks[task_2].append(task_1)
    
    task_and_team = {task: [] for task in available_task}
    for task, team in C:
        task_and_team[task].append(team)

    return n, q, Q, d, m, s, c, C, pre_tasks, task_and_team

def check_constraint(results, Q, s, pre_tasks):
    completion_time = {task: 0 for task in range(n)}

    for task, team, start_time in results:
        completion_time[task] = start_time + d[task]

    for task, team, start_time in results:
        for pre_task in pre_tasks[task]:
            if completion_time[pre_task] > start_time:
                print(f'Task {pre_task+1} is done at {completion_time[pre_task]} but task {task+1} is assigned to team {team+1} at {start_time}')
        
        if start_time < s[team]:
            print(f'Task {task+1} is assigned to team {team+1} at {start_time} but team {team+1} is available at {s[team]}')


def compare_results(results_1, results_2, d, C) -> bool:
    """Compare results_1 and results_2 
    
    Return True if results_1 is better than results_2, else False
    """
    task_count_1, completion_time_1, cost_1 = calculate_result(results_1, d, C)
    task_count_2, completion_time_2, cost_2 = calculate_result(results_2, d, C)

    if task_count_1 > task_count_2:
        return True
    elif task_count_1 < task_count_2:
        return False
    else:
        if completion_time_1 < completion_time_2:
            return True
        elif completion_time_1 > completion_time_2:
            return False
        else:
            return cost_1 < cost_2

def calculate_result(results, duration, Cost):
    task_count = len(results)

    completion_time = 0
    cost = 0
    for task, team, start_time in results:
        completion_time = max(completion_time, start_time + duration[task])
        cost += Cost[(task, team)]

    return task_count, completion_time, cost

def calculate_start_time(pre_results: list, duration, team_start_time, Q, pre_tasks: dict, n, m):
    results = []
    completion_time_of_task = {task: 1e9 for task in range(n)}
    available_time_of_team = {team: team_start_time[team] for team in range(m)}

    pop_position = 0
    while pre_results:
        task, team = pre_results.pop(pop_position)

        # if pre_task is not completed, then skip, else start time is max of completion time of pre_task and available time of team
        continue_flag = False
        pre_task_complete_time = []
        for pre_task in pre_tasks[task]:
            if completion_time_of_task[pre_task] == 1e9:
                pre_results.insert(pop_position, (task, team))
                pop_position += 1
                continue_flag = True
                break
            if completion_time_of_task[pre_task] > available_time_of_team[team]:
                pre_task_complete_time.append(completion_time_of_task[pre_task])
        
        if continue_flag:
            continue

        if len(pre_task_complete_time) != 0:
            max_pre_task_complete_time = max(pre_task_complete_time)
            start_time = max(max_pre_task_complete_time, available_time_of_team[team])
        else:
            start_time = available_time_of_team[team]

        results.append((task, team, start_time))
        completion_time_of_task[task] = start_time + duration[task]
        available_time_of_team[team] = start_time + duration[task]

        pop_position = 0

    return results

def feasible_result(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team):
    # create a random (task, team) assignment and order then calculate start time
    cost = C.copy()

    pre_results = []
    while cost:
        task, team = random.choice(list(cost.keys()))
        pre_results.append((task, team))
        
        for team in task_and_team[task]:
            cost.pop((task, team))

    results = calculate_start_time(pre_results.copy(), d, s, Q, pre_tasks, n, m)
    return pre_results, results

def tabu_select(best_pre_results, task_and_team, tabu_list: deque, pre_tasks: dict, d, s, Q, n, m, C):
    """
    Return best neighbor of results
    """
    neighbor_results = []
    for i in range(TRY_COUNT_1):
        pre_results_copy = best_pre_results.copy()
        if i % 4 == 0:
            # swap order of (task, team) of 2 random tasks
            id_1 = random.randint(0, len(pre_results_copy) - 1)
            id_2 = random.randint(0, len(pre_results_copy) - 1)
            pre_results_copy[id_1], pre_results_copy[id_2] = pre_results_copy[id_2], pre_results_copy[id_1]

        elif i % 4 == 1:
            # change team of a random task
            for _ in range(TRY_COUNT_2):
                id_1 = random.randint(0, len(pre_results_copy) - 1)
                task, team = pre_results_copy[id_1]
                temp_team = task_and_team[task].copy()
                if len(temp_team) == 1:
                    continue
                temp_team.remove(team)
                new_team = random.choice(temp_team)
                pre_results_copy[id_1] = (task, new_team)
                break

        elif i % 4 == 2:
            # job insert
            # random pick a task and team
            (task, team) = random.choice(pre_results_copy)
            pre_results_copy.remove((task, team))
            position = random.randint(0, len(pre_results_copy))
            pre_results_copy.insert(position, (task, team))

        elif i % 4 == 3:
            # job reversal
            id_1 = random.randint(0, len(pre_results_copy) - 1)
            id_2 = random.randint(0, len(pre_results_copy) - 1)
            if id_1 > id_2:
                id_1, id_2 = id_2, id_1
            
            if id_1 != 0:
                pre_results_copy[id_1:id_2+1] = pre_results_copy[id_2:id_1-1:-1]
            else:
                pre_results_copy[id_1:id_2+1] = pre_results_copy[id_2::-1]

        if tuple(pre_results_copy) in tabu_list:
            continue

        assert len(pre_results_copy) == len(best_pre_results), f'{len(pre_results_copy)} != {len(best_pre_results)}'
            
        neighbor_results.append(calculate_start_time(pre_results_copy, d, s, Q, pre_tasks, n, m))

    best_neighbor = neighbor_results[0]
    best_task_count, best_completion_time, best_cost = calculate_result(best_neighbor, d, C)
    for neighbor in neighbor_results[1:]:
        task_count_new, completion_time_new, cost_new = calculate_result(neighbor, d, C)
        
        if task_count_new > best_task_count:
            best_neighbor = neighbor
        elif task_count_new == best_task_count:
            if completion_time_new < best_completion_time:
                best_neighbor = neighbor
            elif completion_time_new == best_completion_time:
                if cost_new < best_cost:
                    best_neighbor = neighbor

    best_pre_results = []
    for task, team, start_time in best_neighbor:
        best_pre_results.append((task, team))

    return best_neighbor, best_pre_results

def tabu_search(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team, initial_tabu_length=30, max_tabu_length=50, min_tabu_length=10):
    # from greedy import greedy_min_starttime
    # best_results = greedy_min_starttime(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team)
    # best_pre_results = []
    # for task, team, start_time in best_results:
    #     best_pre_results.append((task, team))

    best_pre_results, best_results = feasible_result(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team)

    stuck_count = 0
    tabu_length = initial_tabu_length
    tabu_list = deque(maxlen=tabu_length)

    tabu_list.append(best_pre_results) # only save pre_results, not results
    start_time_TS = time.time()
    results_log = []
    # while time.time() - start_time_TS < TIME_LIMIT and stuck_count < STUCK_COUNT_LIMIT:
    while stuck_count < STUCK_COUNT_LIMIT:
    # while time.time() - start_time_TS < TIME_LIMIT:
        stuck_count += 1
        results, pre_results = tabu_select(best_pre_results.copy(), task_and_team, tabu_list, pre_tasks, d, s, Q, n, m, C)

        if compare_results(results, best_results, d, C):
            best_pre_results = pre_results
            best_results = results
            stuck_count = 0
            tabu_list.append(best_pre_results)
            # results_log.append(calculate_result(best_results, d, C))
            # print(calculate_result(results, d, C))
            # check_constraint(best_results, Q, s, pre_tasks)
            # Decrease Tabu Length for exploitation
            tabu_length = max(min_tabu_length, tabu_length - 1)
            tabu_list = deque(tabu_list, maxlen=tabu_length)

        else:
            # Increase Tabu Length for exploration if stuck
            if stuck_count >= 5:  # Adjust threshold as needed
                tabu_length = min(max_tabu_length, tabu_length + 1)
                tabu_list = deque(tabu_list, maxlen=tabu_length)

    return best_results
    # return best_results, results_log

if __name__ == '__main__':
    n, q, Q, d, m, s, c, C, pre_tasks, task_and_team = my_input()
    results = tabu_search(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team)
    print(len(results))
    for task, team, start_time in results:
        print(task+1, team+1, start_time)

    # check_constraint(results, Q, s, pre_tasks)    
    print(calculate_result(results, d, C))