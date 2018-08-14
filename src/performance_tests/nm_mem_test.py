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

subprocess.call(args, shell=False)
print("finished running all simulations")

