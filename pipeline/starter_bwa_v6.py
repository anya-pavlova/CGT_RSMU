import glob
import os
import subprocess
import sys

path = sys.argv[1]

for filename in glob.glob(path + "/*"):
    subprocess.Popen(["sudo", "python3.5", "/home/bioinf/pipeline/full_pipe_bwa_edition_V6_pls_sort.py",
                      filename, "coverage"], stdout=open(filename+"/out", 'a'), stderr=open(filename+"/err", 'a'))
