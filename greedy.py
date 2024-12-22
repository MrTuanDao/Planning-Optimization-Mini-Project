TIME_LIMIT = 5 # seconds

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
        
#--------------------------------------------------------------------------------
def greedy_min_starttime(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team):
    Cost = C.copy()
    results = [] # (task, team, start_time)
    
    available_time = {team: s[team] for team in range(m)}
    completion_time = {task: 1e9 for task in range(n)}

    task_do_not_have_pre_task = set()
    for task in pre_tasks.keys():
        if len(pre_tasks[task]) == 0:
            task_do_not_have_pre_task.add(task)

    for task in task_do_not_have_pre_task:
        min_available_time = 1e9
        min_available_team = -1
        min_cost = 1e9
        for team in task_and_team[task]:
            if available_time[team] == min_available_time and Cost[(task, team)] < min_cost:
                min_available_time = available_time[team]
                min_available_team = team
                min_cost = Cost[(task, team)]
                continue

            if available_time[team] < min_available_time:
                min_available_time = available_time[team]
                min_available_team = team
                min_cost = Cost[(task, team)]
                continue
                
        assert min_available_team != -1, 'All tasks do not have pre-task should be assigned to a team'

        available_time[min_available_team] = min_available_time + d[task]
        completion_time[task] = available_time[min_available_team]
        results.append((task, min_available_team, min_available_time))
        
        for team in task_and_team[task]:
            Cost.pop((task, team))

    start_time_ = time.time()
    while Cost and time.time() - start_time_ < TIME_LIMIT:        
        # get team and task that has least available time
        min_available_time = 1e9
        min_available_team = -1
        min_available_task = -1
        min_cost = 1e9
        # pre_task_completion_time = []
        # pre_task = []
        for (task, team) in Cost:
            continue_flag_if_pre_task_not_done = False
            # check at this time, pre task of task is done yet
            cur_time = available_time[team]
            pre_task_completion_time = []

            for task_1 in pre_tasks[task]:
                # max of all pre-task completion time
                if completion_time[task_1] > cur_time:
                    continue_flag_if_pre_task_not_done = True
                    pre_task_completion_time.append(completion_time[task_1])

            max_pre_task_completion_time = max(pre_task_completion_time) if pre_task_completion_time else 1e9
            if max_pre_task_completion_time < min_available_time:
                min_available_time = max_pre_task_completion_time
                min_available_team = team
                min_available_task = task
                min_cost = Cost[(task, team)]
                continue

            if max_pre_task_completion_time == min_available_time and Cost[(task, team)] < min_cost:
                min_available_team = team
                min_available_task = task
                min_cost = Cost[(task, team)]
                continue

            if continue_flag_if_pre_task_not_done:
                continue

            if available_time[team] < min_available_time:  
                min_available_time = available_time[team]
                min_available_team = team
                min_available_task = task
                min_cost = Cost[(task, team)]
                continue

            if available_time[team] == min_available_time and Cost[(task, team)] < min_cost:
                min_available_time = available_time[team]
                min_available_team = team
                min_available_task = task
                min_cost = Cost[(task, team)]
                continue


        # assign task to team
        available_time[min_available_team] = min_available_time + d[min_available_task]
        completion_time[min_available_task] = available_time[min_available_team]
        for team in task_and_team[min_available_task]:
            Cost.pop((min_available_task, team))

        results.append((min_available_task, min_available_team, available_time[min_available_team] - d[min_available_task]))

    print(len(results))
    for task, team, start_time in results:
        print(task+1, team+1, start_time)
    
    return results

def check_constraint(results, Q):
    completion_time = {task: 0 for task in range(n)}

    for task, team, start_time in results:
        completion_time[task] = start_time + d[task]

    for task, team, start_time in results:
        for task_1, task_2 in Q:
            if task_2 == task:
                if completion_time[task_1] > start_time:
                    print(f'Task {task_1+1} is done at {completion_time[task_1]} but task {task+1} is assigned to team {team} at {start_time}')

def calculate_result(results, duration, Cost):
    task_count = len(results)

    completion_time = 0
    cost = 0
    for task, team, start_time in results:
        completion_time = max(completion_time, start_time + duration[task])
        cost += Cost[(task, team)]

    return task_count, completion_time, cost

if __name__=='__main__':
    n, q, Q, d, m, s, c, C, pre_tasks, task_and_team = my_input()
    results = greedy_min_starttime(n, q, Q, d, m, s, c, C, pre_tasks, task_and_team)
    # check_constraint(results, Q)
    
    # print(calculate_result(results, d, C))