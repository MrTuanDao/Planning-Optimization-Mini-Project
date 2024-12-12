INITIAL_POPULATION_SIZE = 20
MAX_POPULATION_SIZE = 50
MAX_GENERATION = 100
STUCK_GENERATION_LIMIT = 10

FIND_NEIGHBOR_TRY = 100
CHANGE_TEAM_TRY = 100

import random

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


def compare_results(results_1, results_2, d, C) -> bool:
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
    assigned_task = {task: False for task in range(n)}

    pop_position = 0
    while pre_results:
        if pop_position >= len(pre_results):
            break

        task, team = pre_results.pop(pop_position)
        if assigned_task[task]:
            continue

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
        assigned_task[task] = True
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

def task_and_team_pair(C):
    task_and_team = {}
    for task, team in C:
        if task not in task_and_team:
            task_and_team[task] = []
        task_and_team[task].append(team)
    return task_and_team

def crossover(parent_1, parent_2):
    pre_results_1 = []
    pre_results_2 = []

    for task, team, start_time in parent_1:
        pre_results_1.append((task, team))

    for task, team, start_time in parent_2:
        pre_results_2.append((task, team))

    len_pre_results_1 = len(pre_results_1)
    len_pre_results_2 = len(pre_results_2)
    child_1 = pre_results_1[:len_pre_results_1 // 2] + pre_results_2[len_pre_results_2 // 2:]
    child_2 = pre_results_2[:len_pre_results_2 // 2] + pre_results_1[len_pre_results_1 // 2:]

    child_1 = calculate_start_time(child_1, d, s, Q)
    child_2 = calculate_start_time(child_2, d, s, Q)

    return child_1, child_2

def mutation(parent):
    pre_results = []
    for task, team, start_time in parent:
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

def GA(Q, d, s, C, task_and_team):
    best_result = feasible_result(Q, d, s, C)

    population_size = INITIAL_POPULATION_SIZE
    # create a random population
    population = []
    for _ in range(population_size):
        population.append(feasible_result(Q, d, s, C))

    generation = 0
    while generation < MAX_GENERATION:
        # select the best population
        best_population = sorted(population, key=lambda x: (-calculate_result(x, d, C)[0], calculate_result(x, d, C)[1], calculate_result(x, d, C)[2]))[:population_size // 2]

        # crossover
        for _ in range(population_size // 2):
            parent_1, parent_2 = random.sample(best_population, 2)
            child_1, child_2 = crossover(parent_1, parent_2)
            population.append(child_1)
            population.append(child_2)

        # mutation
        for _ in range(population_size // 2):
            parent_1 = random.choice(best_population)
            child_1 = mutation(parent_1)
            population.append(child_1)


        # update best result
        pre_best_result = best_result
        best_result = sorted(population + [best_result], key=lambda x: (-calculate_result(x, d, C)[0], calculate_result(x, d, C)[1], calculate_result(x, d, C)[2]))[0]

        if pre_best_result == best_result:
            stuck_generation += 1
        else:
            # print(f'Improvement in generation {generation} from {calculate_result(pre_best_result, d, C)} to {calculate_result(best_result, d, C)}')
            stuck_generation = 0

        if stuck_generation >= STUCK_GENERATION_LIMIT:
            break

        # update population size
        population_size = len(population)
        if population_size > MAX_POPULATION_SIZE:
            population = random.sample(population, INITIAL_POPULATION_SIZE)
            population_size = len(population)

        generation += 1

    return best_result

if __name__ == '__main__':
    # random.seed(8)
    n, q, Q, d, m, s, c, C = my_input()
    task_and_team = task_and_team_pair(C)
    results = GA(Q, d, s, C, task_and_team)
    print(len(results))
    for task, team, start_time in results:
        print(task+1, team+1, start_time)

    check_constraint(results, Q, s)    
    # print(calculate_result(results, d, C))

    # for seed in range(100):
    #     random.seed(seed)
    #     results = GA(Q, d, s, C, task_and_team)

    #     print(seed)
    #     check_constraint(results, Q, s)
