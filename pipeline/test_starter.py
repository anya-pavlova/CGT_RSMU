import glob
import os
import subprocess
import sys

path = sys.argv[1]

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] not in ["nohup.out"]:
        subprocess.Popen(["sudo", "python3.5", "/home/bioinf/pipeline/new_pipe_for_testing.py",
                          filename, "coverage"], stdout=open(filename + "/out", 'a'),
                         stderr=open(filename + "/err", 'a'))
