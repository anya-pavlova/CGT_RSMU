import glob
import os
import subprocess
import sys

path = sys.argv[1]
if sys.argv[1][-1:] == "/":
    path = sys.argv[1][:-1]
choose_ur_bed = sys.argv[2]

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] not in ["nohup.out", "test"]:
        print(filename)
        subprocess.Popen(["sudo", "python3.5", "/home/bioinf/pipeline/test_pipe.py",
                          filename, "analysis", choose_ur_bed], stdout=open(filename + "/hz.txt", 'a'),
                         stderr=open(filename + "/nohup.out", 'a'))
