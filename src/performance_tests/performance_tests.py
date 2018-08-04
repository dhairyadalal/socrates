import subprocess
from time import time, strftime, localtime
from datetime import timedelta
import pandas as pd

run = "python run_simulator.py -s 1 -p sample_domains/restaurant/simulation_config.yml -t yaml -nv"
args = run.split()

def secondsToStr(elapsed=None):
    if elapsed is None:
        return strftime("%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))

elapsed_times = []
for i in [1, 10, 50, 100, 500, 1000]:
    print("on round: ", i)
    args[3] = str(i)
    start = time()
    subprocess.call(args, shell=False)
    end = time()
    elapsed_times.append({"n": i, "time": secondsToStr(end-start)})
    pd.DataFrame(elapsed_times).to_csv("nm_times.csv", index=False)

print("finished running all simulations")

