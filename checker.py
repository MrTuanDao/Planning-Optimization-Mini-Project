import subprocess
import sys

def read_tc(tc_file):
    lines = open(tc_file).read().strip().split('\n')
    n, q = map(int, lines[0].split())
    Q = []
    for line in lines[1:q+1]:
        task_1, task_2 = map(int, line.split())
        Q.append((task_1-1, task_2-1))
    d = list(map(int, lines[q+1].split()))
    m = int(lines[q+2])
    s = list(map(int, lines[q+3].split()))
    c = int(lines[q+4])
    C = {}
    for line in lines[q+5:]:
        i, j, cost = map(int, line.split())
        C[(i-1, j-1)] = cost
    return n, q, Q, d, m, s, c, C

def check(output, rs, tc_file, Q):
    # check constraint of output
    lines = output.split('\n')
    completion_time = {task: 0 for task in range(n)}

    results = []
    for line in lines[1:]:
        task, team, start_time = map(int, line.split())
        results.append((task-1, team-1, start_time))
        completion_time[task-1] = start_time + d[task-1]

    for task, team, start_time in results:
        for task_1, task_2 in Q:
            if task_2 == task:
                if completion_time[task_1] > start_time:
                    print(f'Testcase {tc_file} failed. \
                          Task {task_1+1} is done at {completion_time[task_1]} but task {task+1} is assigned to team {team} at {start_time}')
                    return False


    sol_task_count, sol_completion_time, sol_cost = compute_solution(output, task_duration, cost_matrix)
    rs_task_count, rs_completion_time, rs_cost = compute_solution(rs, task_duration, cost_matrix)

    # print(sol_task_count, sol_completion_time, sol_cost)
    # print(rs_task_count, rs_completion_time, rs_cost)
    if sol_task_count >= rs_task_count and sol_completion_time <= rs_completion_time and sol_cost <= rs_cost:
        print(f'Testcase {tc_file} passed. \
              Jury solution: {rs_task_count} {rs_completion_time} {rs_cost}, \
              Participant solution: {sol_task_count} {sol_completion_time} {sol_cost}')
        return True
    else:
        print(f'Testcase {tc_file} failed. \
              Jury solution: {rs_task_count} {rs_completion_time} {rs_cost}, \
              Participant solution: {sol_task_count} {sol_completion_time} {sol_cost}')
        return False
    
def calculate_result(results, duration, Cost):
    task_count = len(results)

    completion_time = 0
    cost = 0
    for task, team, start_time in results:
        completion_time = max(completion_time, start_time + duration[task])
        cost += Cost[(task, team)]

    return task_count, completion_time, cost

def compute_solution(sol, task_duration, cost_matrix):
    lines = sol.split('\n')
    task_count = int(lines[0])

    completion_time = 0
    cost = 0
    for line in lines[1:]:
        task_id, team_id, start_time = map(int, line.split())
        completion_time = max(completion_time, start_time + task_duration[task_id-1])
        cost += cost_matrix[(task_id-1, team_id-1)]

    return task_count, completion_time, cost


if __name__ == '__main__':
    # score = 0
    # for i in range(1, 11):        
    #     tc_file = f'testcases/tc_{i}.txt'
    #     n, q, Q, d, m, s, c, C = read_tc(tc_file)
    #     task_duration = d
    #     cost_matrix = C

    #     rs_file = f'testcases/rs_{i}.txt'
    #     rs = open(rs_file).read().strip()

    #     result = subprocess.run(['python3', method], stdin=open(tc_file), capture_output=True, text=True)
    #     output = result.stdout
        
    #     try:    
    #         if check(output.strip(), rs.strip(), tc_file, Q):
    #             score += 100
    #     except Exception as e:
    #         print(f'Testcase {tc_file} error: {e}')
    #         import traceback
    #         traceback.print_exc()
    #         break

    # print(f'Score: {score}/1000')
    # with open(f'results/{method[:-3]}.txt', 'a') as f:
    #     f.write(f'{score}\n')

    import os
    import time
    file_name = [f for f in os.listdir('synthetic_data') if f.startswith('tc_')]
    methods = ['ilp', 'cp', 'greedy', 'local_search_team_and_order', 'tabu_search', 'simulated_annealing', 'GA', 'local_search_time']

    for method in methods:
        for file in file_name:
            tc_file = f'synthetic_data/{file}'
            n, q, Q, d, m, s, c, C = read_tc(tc_file)
            task_duration = d
            cost_matrix = C

            for i in range(10):
                time_start = time.time()
                result = subprocess.run(['python3', f'{method}.py'], stdin=open(tc_file), capture_output=True, text=True)
                output = result.stdout
                time_end = time.time()
                results = []
                for line in output.split('\n')[1:-1]:
                    task, team, start_time = map(int, line.split())
                    results.append((task-1, team-1, start_time))

                max_task_count, min_completion_time, min_cost = calculate_result(results, task_duration, cost_matrix)
                print(f'{file}, {method}, {max_task_count}, {min_completion_time}, {min_cost}, {time_end - time_start}')
                with open(f'synthetic_data/{method + "_" + file}', 'a') as f:
                    f.write(f'{max_task_count}, {min_completion_time}, {min_cost}, {time_end - time_start}\n')
            # exit()