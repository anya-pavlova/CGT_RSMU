import glob
import os
import subprocess
import sys

path = sys.argv[1]

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] != "nohup.out":
        print(filename)
        subprocess.Popen(["sudo", "python3.5", "/home/bioinf/scripts/pipe_V6_one_queue.py",
                          filename, "coverage"], stdout=open(filename + "/out", 'a'),
                         stderr=open(filename + "/err", 'a'))
