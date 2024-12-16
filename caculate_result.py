import os

import numpy as np

file_names = [f for f in os.listdir('synthetic_data') if not f.startswith('tc_')]
caculated_results = []

for file in file_names:
    values = file.split('_')

    N = values[-3]
    method = '_'.join(values[:-5])

    max_task_counts = []
    min_completion_times = []
    min_costs = []
    times = []
    with open(f'synthetic_data/{file}', 'r') as f:
        for line in f:
            max_task_count, min_completion_time, min_cost, time = map(float, line.strip().split(','))
            max_task_counts.append(max_task_count)
            min_completion_times.append(min_completion_time)
            min_costs.append(min_cost)
            # times.append(round(time, 2))

    avg_max_task_count = sum(max_task_counts) / len(max_task_counts)
    avg_min_completion_time = sum(min_completion_times) / len(min_completion_times)
    avg_min_cost = sum(min_costs) / len(min_costs)
    # avg_time = sum(times) / len(times)

    std_max_task_count = np.std(max_task_counts)
    std_min_completion_time = np.std(min_completion_times)
    std_min_cost = np.std(min_costs)
    # std_time = np.std(times)

    caculated_results.append(f'{N}, {method}, {avg_max_task_count}, {std_max_task_count:.2f}, {avg_min_completion_time:.2f}, {std_min_completion_time:.2f}, {avg_min_cost:.2f}, {std_min_cost:.2f}')

caculated_results.sort(key=lambda x: (x.split(',')[0], x.split(',')[1]))

with open('caculated_results.csv', 'w') as f:
    f.write('N, method, avg_max_task_count, std_max_task_count, avg_min_completion_time, std_min_completion_time, avg_min_cost, std_min_cost\n')
    for result in caculated_results:
        f.write(result + '\n')
