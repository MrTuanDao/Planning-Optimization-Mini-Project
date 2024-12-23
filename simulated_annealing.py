FIND_NEIGHBOR_TRY = 100
CHANGE_TEAM_TRY = 100
STUCK_COUNT_LIMIT = 100
TIME_LIMIT = 5 # seconds

import math
import random
import time

def my_input():
    # number of tasks, number of constraints
    n, q = map(int, input().split())

    # constraints pairs, (i, j) means task i must be completed before task
    pre_tasks = {task: [] for task in range(n)}
    post_tasks = {task: [] for task in range(n)}
    Q = []
    for _ in range(q):
        i, j = map(int, input().split())
        Q.append((i-1, j-1))
        pre_tasks[j-1].append(i-1)
        post_tasks[i-1].append(j-1)

    # duration of each task
    d = list(map(int, input().split()))

    # number of teams
    m = int(input())

    # available time points of each team
    s = list(map(int, input().split()))

    # cost if team i is assigned to task j
    c = int(input())
    C = {}
    task_and_team = {}
    for _ in range(c):
        i, j, cost = map(int, input().split())
        C[(i-1, j-1)] = cost
        task_and_team[i-1] = task_and_team.get(i-1, []) + [j-1]

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

    def find_dependent_tasks(cycles):
        # Tìm tất cả các task phụ thuộc vào các task trong cycle
        dependent_tasks = set(cycles)
        queue = list(cycles)
        
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

    pre_tasks = {task: [] for task in available_task}
    for task_1, task_2 in Q:
        pre_tasks[task_2].append(task_1)

    task_and_team = {task: [] for task in available_task}
    for task, team in C:
        task_and_team[task].append(team)

    # return n, q, Q, d, m, s, c, C, pre_tasks, task_and_team

    return n, q, Q, d, m, s, c, C

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


def compare_results(results_1, results_2) -> bool:
    """Compare results_1 and results_2 
    
    Return True if results_1 is better than results_2, else False
    """
    if results_1 is None:
        return False
    if results_2 is None:
        return True

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

def neighbor_result(results, task_and_team):
    pre_results = []
    for task, team, start_time in results:
        pre_results.append((task, team))
    
    cannot_find_neighbor = True
    for _ in range(FIND_NEIGHBOR_TRY):
        # swap order of (task, team) of 2 random tasks
        id_1 = random.randint(0, len(pre_results) - 1)
        id_2 = random.randint(0, len(pre_results) - 1)
        pre_results[id_1], pre_results[id_2] = pre_results[id_2], pre_results[id_1]

        # change team of a random task
        all_task_have_1_team = True
        for _ in range(CHANGE_TEAM_TRY):
            id_1 = random.randint(0, len(pre_results) - 1)
            task, team = pre_results[id_1]
            temp_team = task_and_team[task].copy()
            if len(temp_team) == 1:
                continue
            temp_team.remove(team)
            new_team = random.choice(temp_team)
            pre_results[id_1] = (task, new_team)
            all_task_have_1_team = False
            break

        if all_task_have_1_team:
            cannot_find_neighbor = True
            break

        results = calculate_start_time(pre_results, d, s, Q)

        cannot_find_neighbor = False
        break

    if cannot_find_neighbor:
        return None
    else:
        return results
    
def S_Metropolis(current_result, task_and_team, temperature, Q, d, s, C):
    neighbor = neighbor_result(current_result, task_and_team)
    if neighbor is None:
        return current_result
    
    task_count_1, completion_time_1, cost_1 = calculate_result(current_result, d, C)
    task_count_2, completion_time_2, cost_2 = calculate_result(neighbor, d, C)

    assert task_count_1 == task_count_2, "All solutions must have the same number of tasks"

    if completion_time_1 < completion_time_2:
        return current_result
    elif completion_time_1 == completion_time_2:
        if cost_1 <= cost_2:
            return current_result
        else:
            probability = 1 / math.exp((cost_2 - cost_1) / cost_2 / temperature)
    else:
        probability = math.exp((completion_time_2 - completion_time_1) / completion_time_2 / temperature)
    
    if random.random() < probability:
        return feasible_result(Q, d, s, C)
    else:
        return neighbor

def simulated_annealing(Q, d, s, C, task_and_team):
    results = feasible_result(Q, d, s, C)
    global_best_results = results.copy()
    local_best_results = results.copy()

    temperature = 1
    stuck_count = 0
    start_time_SA = time.time()
    while time.time() - start_time_SA < TIME_LIMIT:
        results = S_Metropolis(local_best_results, task_and_team, temperature, Q, d, s, C)
        temperature *= 0.99

        if compare_results(results, local_best_results):
            # print(f'Improvement: {calculate_result(results, d, C)} from {calculate_result(best_results, d, C)}')
            local_best_results = results
            if compare_results(local_best_results, global_best_results):
                global_best_results = local_best_results
            stuck_count = 0
        else:
            stuck_count += 1

        if stuck_count > STUCK_COUNT_LIMIT:
            break

    return global_best_results

def task_and_team_pair(C):
    task_and_team = {}
    for task, team in C:
        if task not in task_and_team:
            task_and_team[task] = []
        task_and_team[task].append(team)
    return task_and_team

if __name__ == '__main__':
    n, q, Q, d, m, s, c, C = my_input()
    task_and_team = task_and_team_pair(C)
    results = simulated_annealing(Q, d, s, C, task_and_team)
    print(len(results))
    for task, team, start_time in results:
        print(task+1, team+1, start_time)

    # check_constraint(results, Q, s)    
    print(calculate_result(results, d, C))
