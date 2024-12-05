import subprocess
import sys

method = sys.argv[1]

def read_tc(tc_file):
    lines = open(tc_file).read().strip().split('\n')
    n, q = map(int, lines[0].split())
    Q = [tuple(map(int, line.split())) for line in lines[1:q+1]]
    d = list(map(int, lines[q+1].split()))
    m = int(lines[q+2])
    s = list(map(int, lines[q+3].split()))
    c = int(lines[q+4])
    C = {}
    for line in lines[q+5:]:
        i, j, cost = map(int, line.split())
        C[(i-1, j-1)] = cost
    return n, q, Q, d, m, s, c, C

def check(output, rs, tc_file):
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
    score = 0
    for i in range(1, 11):        
        tc_file = f'testcases/tc_{i}.txt'
        n, q, Q, d, m, s, c, C = read_tc(tc_file)
        task_duration = d
        cost_matrix = C

        rs_file = f'testcases/rs_{i}.txt'
        rs = open(rs_file).read().strip()

        result = subprocess.run(['python3', method], stdin=open(tc_file), capture_output=True, text=True)
        output = result.stdout
        
        try:    
            if check(output.strip(), rs.strip(), tc_file):
                score += 100
        except:
            print(f'Testcase {tc_file} error')
            print(output)

    print(f'Score: {score}/1000')
    with open(f'results/{method[:-3]}.txt', 'a') as f:
        f.write(f'{score}\n')
