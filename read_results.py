import os
import numpy as np
import pandas as pd

file_names = os.listdir('results')

for file_name in file_names:
    df = pd.read_csv(f'results/{file_name}')
    if df.empty:
        continue
    score = df['Score']
    min_score = min(score)
    max_score = max(score)
    avg_score = sum(score) / len(score)
    std_score = np.std(score)
    print(f'{file_name}: {min_score} - {max_score} - {avg_score} - {std_score}')