import subprocess
import sys

method = sys.argv[1]

for i in range(1, 11):        
    tc_file = f'testcases/tc_{i}.txt'
    rs_file = f'testcases/rs_{i}.txt'

    result = subprocess.run(['python3', method], stdin=open(tc_file), capture_output=True, text=True)
    output = result.stdout
    # print(type(output))
    break
