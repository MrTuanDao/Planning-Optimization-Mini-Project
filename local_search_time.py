EARLY_STOP_COUNT = 100
TIME_LIMIT = 5 # seconds

import random
import time

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

    for task_1, task_2 in Q.copy():
        if task_1 not in available_task or task_2 not in available_task:
            Q.remove((task_1, task_2))

    return n, q, Q, d, m, s, c, C, cycles

#--------------------------------------------------------------------------------

def feasible_result(Q, d, s, C):
    # create a random (task, team) assignment and order then calculate start time
    cost = C.copy()

    pre_results = []
    while cost:
        task, team = random.choice(list(cost.keys()))
        pre_results.append((task, team))
        
        for task_1, team_1 in cost.copy():
            if task_1 == task:
                cost.pop((task_1, team_1))

    results = calculate_start_time(pre_results, d, s, Q)
    return results

def calculate_start_time(pre_results: list, duration, team_start_time, Q):
    results = []
    completion_time_of_task = {task: 1e9 for task in range(n)}
    available_time_of_team = {team: team_start_time[team] for team in range(m)}

    pop_position = 0
    while pre_results:
        task, team = pre_results.pop(pop_position)

        # if pre_task is not completed, then skip, else start time is max of completion time of pre_task and available time of team
        continue_flag = False
        pre_task_complete_time = []
        for task_1, task_2 in Q:
            if task_2 == task:
                if completion_time_of_task[task_1] == 1e9:
                    pre_results.insert(pop_position, (task_2, team))
                    pop_position += 1
                    continue_flag = True
                    break
                if completion_time_of_task[task_1] > available_time_of_team[team]:
                    pre_task_complete_time.append(completion_time_of_task[task_1])
        
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

def check_constraint(results, Q, s):
    completion_time = {task: 0 for task in range(n)}

    for task, team, start_time in results:
        completion_time[task] = start_time + d[task]

    for task, team, start_time in results:
        for task_1, task_2 in Q:
            if task_2 == task:
                if completion_time[task_1] > start_time:
                    print(f'Task {task_1+1} is done at {completion_time[task_1]} but task {task+1} is assigned to team {team+1} at {start_time}')
        
        if start_time < s[team]:
            print(f'Task {task+1} is assigned to team {team+1} at {start_time} but team {team+1} is available at {s[team]}')

def calculate_result(results, duration, Cost):
    task_count = len(results)

    completion_time = 0
    cost = 0
    for task, team, start_time in results:
        completion_time = max(completion_time, start_time + duration[task])
        cost += Cost[(task, team)]

    return task_count, completion_time, cost

def local_search(results, n, q, Q, d, m, s, c, Cost, cycles):
    # pick random a timepoint, for each result after this timepoint, swap 2 task, team, so that the result is valid: Q and purpose is min cost
    COST = Cost.copy()
    new_results = {}
    for task, team, start_time in results:
        new_results[(task, team)] = start_time
    results = new_results


    early_stop_count = EARLY_STOP_COUNT
    start_time_LS = time.time()
    while time.time() - start_time_LS < TIME_LIMIT:
        max_time = 0
        for (task, team), start_time in results.items():
            if start_time > max_time:
                max_time = start_time

        random_timepoint = random.randint(0, max_time)

        # caculate completion time of all task
        start_time_of_task = {task: 0 for task in range(n)}
        completion_time_of_task = {task: 0 for task in range(n)}
        available_time_of_team = {team: 1e9 for team in range(m)}
        for (task, team), start_time in results.items():
            start_time_of_task[task] = start_time
            completion_time_of_task[task] = start_time + d[task]
            if completion_time_of_task[task] < random_timepoint:
                available_time_of_team[team] = start_time + d[task]

        # find all task that do not have pre-task after this timepoint
        task_and_team = [(task, team) for (task, team), start_time in results.items()]
        task_do_not_have_pre_task = []
        for task, team in task_and_team:
            continue_flag = False
            for task_1, task_2 in Q:
                if task_2 == task:
                    if completion_time_of_task[task_1] > random_timepoint or completion_time_of_task[task_2] < random_timepoint:
                        continue_flag = True
                        break

            if not continue_flag:
                task_do_not_have_pre_task.append((task, team))
        
        # print(random_timepoint, task_do_not_have_pre_task, completion_time_of_task, start_time_of_task)
        
        # compare cost of all task that do not have pre-task after this timepoint, team that nearest to this timepoint, can be swapped
        discount_cost = 0
        min_cost_task_1 = -1
        min_cost_task_2 = -1
        min_cost_team_1 = -1
        min_cost_team_2 = -1
        for task_1, team_1 in task_do_not_have_pre_task:
            for task_2, team_2 in task_do_not_have_pre_task:
                if start_time_of_task[task_1] < s[team_2] or start_time_of_task[task_2] < s[team_1]:
                    continue
                
                if (task_1, team_2) in C and (task_2, team_1) in C:
                    cur_cost = C[(task_1, team_1)] + C[(task_2, team_2)]
                    new_cost = C[(task_1, team_2)] + C[(task_2, team_1)]
                    if discount_cost < cur_cost - new_cost:
                        discount_cost = cur_cost - new_cost
                        min_cost_task_1 = task_1
                        min_cost_task_2 = task_2
                        min_cost_team_1 = team_1
                        min_cost_team_2 = team_2
        
        if discount_cost > 0:
            results.pop((min_cost_task_1, min_cost_team_1))
            results.pop((min_cost_task_2, min_cost_team_2))
            results[(min_cost_task_1, min_cost_team_2)] = start_time_of_task[min_cost_task_1]
            results[(min_cost_task_2, min_cost_team_1)] = start_time_of_task[min_cost_task_2]
            early_stop_count = EARLY_STOP_COUNT
        else:
            early_stop_count -= 1
            if early_stop_count == 0:
                break

    # convert to list
    new_results = []
    for (task, team), start_time in results.items():
        new_results.append((task, team, start_time))
    return new_results

if __name__=='__main__':
    n, q, Q, d, m, s, c, C, cycles = my_input()
    results = feasible_result(Q.copy(), d, s, C.copy())
    results = local_search(results, n, q, Q, d, m, s, c, C, cycles)

    # check_constraint(results, Q, s)
    # print(calculate_result(results, d, C))
    
    print(len(results))
    for task, team, start_time in results:
        print(task+1, team+1, start_time)
