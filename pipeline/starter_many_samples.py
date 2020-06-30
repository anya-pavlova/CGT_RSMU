import glob
import os
import subprocess
import sys

path = sys.argv[1]
from_here = sys.argv[2]
to_here = sys.argv[3]

for filename in glob.glob(path + "/*"):
    if filename.split("/")[-1] not in ["nohup.out", "test", "tabl.csv"]:
        subprocess.Popen(["python3.8", "/data/CGT_RSMU/pipeline/exome_pipe_many_samples.py",
                          filename, from_here, to_here], stdout=open(filename + "/out", 'a'),
                         stderr=open(filename + "/err", 'a'))